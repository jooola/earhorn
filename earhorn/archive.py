from pathlib import Path
from subprocess import DEVNULL, run
from threading import Thread
from typing import Optional

from loguru import logger

from ._ffmpeg import FFMPEG

TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"


class Archiver(Thread):
    name = "archiver"
    url: str
    path: Path
    segment_size: int
    segment_filename: str
    segment_format: str
    segment_format_options: Optional[str]
    copy_stream: bool

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        url: str,
        path: Path,
        segment_size: int,
        segment_filename: str,
        segment_format: str,
        segment_format_options: Optional[str],
        copy_stream: bool,
    ):
        Thread.__init__(self)
        self.url = url

        if not path.is_dir():
            raise ValueError(f"archive path '{path}' is not a directory!")
        self.path = path

        self.segment_size = segment_size
        self.segment_filename = segment_filename
        self.segment_format = segment_format
        self.segment_format_options = segment_format_options
        self.copy_stream = copy_stream

    def run(self):
        logger.info("starting archiver")

        cmd = [FFMPEG, "-hide_banner", "-nostats"]

        cmd += ("-re", "-i", self.url)
        cmd += ("-vn",)  # Drop video
        if self.copy_stream:
            logger.info("enabling stream copy")
            cmd += ("-c", "copy")

        cmd += ("-map", "0")
        cmd += ("-map_metadata", "-1")

        cmd += ("-f", "segment")
        cmd += ("-strftime", "1")
        cmd += ("-segment_time", str(self.segment_size))
        cmd += ("-segment_format", self.segment_format)
        if self.segment_format_options:
            cmd += ("-segment_format_options", self.segment_format_options)
        cmd += ("-reset_timestamps", "1")
        cmd += (self.path / f"{self.segment_filename}.{self.segment_format}",)

        run(cmd, check=True, stderr=DEVNULL)
        logger.info("archiver stopped")
