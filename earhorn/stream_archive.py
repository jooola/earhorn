import csv
import os
from pathlib import Path
from shutil import move
from subprocess import Popen
from threading import Thread
from typing import List, Optional

from loguru import logger
from typing_extensions import Protocol

DEFAULT_ARCHIVE_SEGMENT_SIZE: int = 3600
DEFAULT_ARCHIVE_SEGMENT_FORMAT: str = "ogg"

DEFAULT_ARCHIVE_SEGMENT_FILEPATH: str = (
    "{year}/{month}/{day}/{hour}{minute}{second}.{format}"
)


class IngestSegmentError(Exception):
    """An error occurred while ingesting a segment"""


class InvalidSegmentFilename(IngestSegmentError):
    """Invalid segment filename"""


# pylint: disable=too-few-public-methods
class ArchiveStorage(Protocol):
    def ingest_segment(self, segment: Path, segment_filepath: Path):
        ...


# pylint: disable=too-few-public-methods
class LocalArchiveStorage:
    path: Path

    def __init__(self, path: str) -> None:
        self.path = Path(path)
        if not self.path.is_dir():
            raise ValueError(f"archive path '{path}' is not a directory!")

    def ingest_segment(self, segment: Path, segment_filepath: Path):
        segment_fullpath = self.path / segment_filepath

        logger.debug(f"moving segment to {segment_fullpath}")
        segment_fullpath.parent.mkdir(parents=True, exist_ok=True)
        move(segment, segment_fullpath)


def _mkfifo(path: Path):
    if path.exists():
        path.unlink()

    logger.debug(f"creating a fifo at {path}")
    os.mkfifo(path)
    logger.debug(f"fifo at {path} created!")


# pylint: disable=too-many-instance-attributes
class ArchiveHandler:
    SEGMENTS_DIR: str = "incoming"
    SEGMENTS_PENDING_DIR: str = "pending"
    SEGMENTS_LIST: str = "segments.csv"
    SEGMENT_PREFIX: str = "segment"
    SEGMENT_STRFTIME: str = "%Y-%m-%d-%H-%M-%S"

    storage: ArchiveStorage

    segment_filepath: str
    segment_size: int
    segment_format: str
    segment_format_options: Optional[str]
    copy_stream: bool

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        storage: ArchiveStorage,
        segment_filepath: str = DEFAULT_ARCHIVE_SEGMENT_FILEPATH,
        segment_size: int = DEFAULT_ARCHIVE_SEGMENT_SIZE,
        segment_format: str = DEFAULT_ARCHIVE_SEGMENT_FORMAT,
        segment_format_options: Optional[str] = None,
        copy_stream: bool = False,
    ):
        self.storage = storage

        self.segment_filepath = segment_filepath
        self.segment_size = segment_size
        self.segment_format = segment_format
        self.segment_format_options = segment_format_options
        self.copy_stream = copy_stream

        self.segments_dir = Path(self.SEGMENTS_DIR)
        self.segments_list = Path(self.SEGMENTS_LIST)
        self.segments_pending_dir = Path(self.SEGMENTS_PENDING_DIR)

        self.segments_dir.mkdir(exist_ok=True)
        self.segments_pending_dir.mkdir(exist_ok=True)

    def _tmp_segment_filename(self) -> Path:
        return Path(
            ".".join(
                [
                    self.SEGMENT_PREFIX,
                    self.SEGMENT_STRFTIME,
                    self.segment_format,
                ]
            )
        )

    def _segment_filepath(self, segment: Path) -> Path:
        try:
            filename_parts = segment.name.split(".")
            datetime_str = filename_parts[1]
            datetime_parts = datetime_str.split("-")

            return Path(
                self.segment_filepath.format(
                    **{
                        "format": self.segment_format,
                        "year": datetime_parts[0],
                        "month": datetime_parts[1],
                        "day": datetime_parts[2],
                        "hour": datetime_parts[3],
                        "minute": datetime_parts[4],
                        "second": datetime_parts[5],
                    }
                )
            )
        except IndexError as error:
            raise InvalidSegmentFilename(
                f"found invalid segment filename {segment.name}"
            ) from error

    def ffmpeg_output(self):
        args = ["-map_metadata", "-1"]

        if self.copy_stream:
            logger.info("enabling stream copy")
            args += ("-c", "copy")

        args += (
            *("-f", "segment"),
            *("-strftime", "1"),
            *("-segment_time", str(self.segment_size)),
            *("-segment_format", self.segment_format),
        )

        if self.segment_format_options:
            args += ("-segment_format_options", self.segment_format_options)

        args += (
            *("-segment_list", str(self.segments_list)),
            *("-reset_timestamps", "1"),
            str(self.segments_dir / self._tmp_segment_filename()),
        )

        return args

    def ingest_pending_segments(self):
        if self.segments_pending_dir.is_dir():
            for segment in self.segments_pending_dir.iterdir():
                try:
                    self.storage.ingest_segment(
                        segment,
                        self._segment_filepath(segment),
                    )
                except IngestSegmentError as exception:
                    logger.error(exception)

                    # Go try to ingest segments from incoming, pending can wait
                    break

    def wait_for_segments(self):
        # Ingest pending segments before starting
        self.ingest_pending_segments()

        with self.segments_list.open(
            buffering=1,
            encoding="utf-8",
        ) as segments_list_fd:
            logger.debug(f"reading segments from {self.segments_list}")
            for row in csv.reader(segments_list_fd):
                segment = self.segments_dir / row[0]
                try:
                    self.storage.ingest_segment(
                        segment,
                        self._segment_filepath(segment),
                    )

                    self.ingest_pending_segments()
                except InvalidSegmentFilename as exception:
                    logger.error(exception)
                    continue
                except IngestSegmentError as exception:
                    logger.error(exception)

                    segment_pending = self.segments_pending_dir / segment.name
                    if segment != segment_pending and not segment_pending.is_file():
                        logger.debug(f"moving {segment} to {segment_pending}")
                        move(segment, segment_pending)

        self.segments_list.unlink()

    def before_listen_start(self):
        _mkfifo(self.segments_list)

    # pylint: disable=unused-argument
    def process_handler(self, threads: List[Thread], process: Popen):
        thread = Thread(target=self.wait_for_segments)
        thread.start()
        threads.append(thread)
