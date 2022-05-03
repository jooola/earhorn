from pathlib import Path
from subprocess import Popen
from threading import Thread
from typing import List, Optional

from loguru import logger

DEFAULT_ARCHIVE_SEGMENT_SIZE: int = 3600
DEFAULT_ARCHIVE_SEGMENT_FILENAME: str = "archive-%Y%m%d_%H%M%S"
DEFAULT_ARCHIVE_SEGMENT_FORMAT: str = "ogg"


# pylint: disable=too-few-public-methods
class ArchiveHandler:
    path: Path
    segment_size: int
    segment_filename: str
    segment_format: str
    segment_format_options: Optional[str]
    copy_stream: bool

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        path: str,
        segment_size: int = DEFAULT_ARCHIVE_SEGMENT_SIZE,
        segment_filename: str = DEFAULT_ARCHIVE_SEGMENT_FILENAME,
        segment_format: str = DEFAULT_ARCHIVE_SEGMENT_FORMAT,
        segment_format_options: Optional[str] = None,
        copy_stream: bool = False,
    ):
        self.path = Path(path)
        if not self.path.is_dir():
            raise ValueError(f"archive path '{path}' is not a directory!")

        self.segment_size = segment_size
        self.segment_filename = segment_filename
        self.segment_format = segment_format
        self.segment_format_options = segment_format_options
        self.copy_stream = copy_stream

    def output_path(self) -> str:
        return str(self.path / f"{self.segment_filename}.{self.segment_format}")

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
            *("-reset_timestamps", "1"),
            self.output_path(),
        )

        return args

    def process_handler(self, threads: List[Thread], process: Popen):
        pass
