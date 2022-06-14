import csv
import os
from pathlib import Path
from shutil import move
from subprocess import Popen
from tempfile import mkdtemp
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
    logger.debug(f"creating a fifo at {path}")
    os.mkfifo(path)
    logger.debug(f"fifo at {path} created!")


# pylint: disable=too-many-instance-attributes
class ArchiveHandler:
    TMP_SEGMENTS_LIST_FILENAME: str = "segments.csv"
    TMP_SEGMENT_PREFIX: str = "segment"
    TMP_SEGMENT_STRFTIME: str = "%Y-%m-%d-%H-%M-%S"

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

        self.tmp_dir = Path(mkdtemp(prefix="earhorn-"))
        self.tmp_segment_list = self.tmp_dir / self.TMP_SEGMENTS_LIST_FILENAME
        _mkfifo(self.tmp_segment_list)

    def _tmp_segment_filename(self) -> Path:
        return Path(
            ".".join(
                [
                    self.TMP_SEGMENT_PREFIX,
                    self.TMP_SEGMENT_STRFTIME,
                    self.segment_format,
                ]
            )
        )

    def _segment_filepath(self, tmp_segment: Path) -> Path:
        parts = tmp_segment.name.split(".")[1].split("-")

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
            *("-segment_list", str(self.tmp_segment_list)),
            *("-reset_timestamps", "1"),
            str(self.tmp_dir / self._tmp_segment_filename()),
        )

        return args

    def wait_for_segments(self):
        with self.tmp_segment_list.open(
            buffering=1,
            encoding="utf-8",
        ) as tmp_segment_list_fd:
            logger.debug(f"reading segments from {self.tmp_segment_list}")
            for row in csv.reader(tmp_segment_list_fd):
                tmp_segment = self.tmp_dir / row[0]

                self.storage.ingest_segment(
                    tmp_segment,
                    self._segment_filepath(tmp_segment),
                )

        self.tmp_segment_list.unlink()

    # pylint: disable=unused-argument
    def process_handler(self, threads: List[Thread], process: Popen):
        thread = Thread(target=self.wait_for_segments)
        thread.start()
        threads.append(thread)
