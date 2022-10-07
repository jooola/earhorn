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


# pylint: disable=too-few-public-methods
class ArchiveStorage(Protocol):
    def ingest_segment(self, tmp_segment: Path, segment_filepath: Path):
        ...


# pylint: disable=too-few-public-methods
class LocalArchiveStorage:
    path: Path

    def __init__(self, path: str) -> None:
        self.path = Path(path)
        if not self.path.is_dir():
            raise ValueError(f"archive path '{path}' is not a directory!")

    def ingest_segment(self, tmp_segment: Path, segment_filepath: Path):
        segment_fullpath = self.path / segment_filepath

        logger.debug(f"moving segment to {segment_fullpath}")
        segment_fullpath.parent.mkdir(parents=True, exist_ok=True)
        move(tmp_segment, segment_fullpath)


def _mkfifo(path: Path):
    if path.exists():
        path.unlink()

    logger.debug(f"creating a fifo at {path}")
    os.mkfifo(path)
    logger.debug(f"fifo at {path} created!")


# pylint: disable=too-many-instance-attributes
class ArchiveHandler:
    SEGMENTS_DIR: str = "segments"
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

        self.segments_dir.mkdir(exist_ok=True)

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
        parts = segment.name.split(".")[1].split("-")

        return Path(
            self.segment_filepath.format(
                **{
                    "format": self.segment_format,
                    "year": parts[0],
                    "month": parts[1],
                    "day": parts[2],
                    "hour": parts[3],
                    "minute": parts[4],
                    "second": parts[5],
                }
            )
        )

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

    def wait_for_segments(self):
        with self.segments_list.open(
            buffering=1,
            encoding="utf-8",
        ) as segments_list_fd:
            logger.debug(f"reading segments from {self.segments_list}")
            for row in csv.reader(segments_list_fd):
                segment = self.segments_dir / row[0]

                self.storage.ingest_segment(
                    segment,
                    self._segment_filepath(segment),
                )

        self.segments_list.unlink()

    def before_listen_start(self):
        _mkfifo(self.segments_list)

    # pylint: disable=unused-argument
    def process_handler(self, threads: List[Thread], process: Popen):
        thread = Thread(target=self.wait_for_segments)
        thread.start()
        threads.append(thread)
