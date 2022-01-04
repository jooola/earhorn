from pathlib import Path
from subprocess import DEVNULL, run
from threading import Thread

from loguru import logger

TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"


class Archiver(Thread):
    name = "archiver"
    url: str
    path: Path
    segment_size: int
    segment_filename: str
    segment_format: str

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        url: str,
        path: Path,
        segment_size: int,
        segment_filename: str,
        segment_format: str,
    ):
        Thread.__init__(self)
        self.url = url

        if not path.is_dir():
            raise ValueError(f"archive path '{path}' is not a directory!")
        self.path = path

        self.segment_size = segment_size
        self.segment_filename = segment_filename
        self.segment_format = segment_format

    def run(self):
        logger.info("starting archiver")
        args = (
            *("ffmpeg", "-hide_banner", "-nostats"),
            *("-re", "-i", self.url),
            "-vn",  # Drop video
            *("-c", "copy"),
            *("-map", "0"),
            *("-map_metadata", "-1"),
            *("-f", "segment"),
            *("-strftime", "1"),
            *("-segment_time", str(self.segment_size)),
            *("-segment_format", self.segment_format),
            *("-reset_timestamps", "1"),
            self.path / self.segment_filename,
        )

        run(args, check=True, stderr=DEVNULL)
        logger.info("archiver stopped")
