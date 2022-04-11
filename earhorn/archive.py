from pathlib import Path
from subprocess import DEVNULL, run
from threading import Thread
from typing import Optional

from loguru import logger

from ._ffmpeg import FFMPEG
import http.client as httplib
from urllib.request import urlparse

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
    s3_archive_url: str

    def url_exists(s3_url):
        _, host, s3_path, _, _, _ = urlparse(s3_url)
        conn = httplib.HTTPConnection(host)
        conn.request('HEAD', s3_path)
        return conn.getresponse().status < 400

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
        s3_archive_url
    ):
        Thread.__init__(self)
        self.url = url

        if not url_exists(s3_archive_url):
            raise ValueError(f"The s3 storage path '{s3_archive_url} is not valid'")
        self.s3_archive_url = s3_archive_url

        if not path.is_dir():
            raise ValueError(f"archive path '{path}' is not a directory!")
        self.path = path

        self.segment_size = segment_size
        self.segment_filename = segment_filename
        self.segment_format = segment_format
        self.segment_format_options = segment_format_options
        self.copy_stream = copy_stream

    def run(self):

        if self.s3_archive_url:
            logger.info("starting archiver")
            s3_cmd = [FFMPEG, "-hide_banner", "-nostats"]
            s3_cmd += ("-re", "-i", self.url)
            s3_cmd += ("-vn",)  # Drop video
            s3_cmd += ("-map", "0")
            s3_cmd += ("-map_metadata", "-1")

            s3_cmd += ("-f", "segment")
            s3_cmd += ("-strftime", "1")
            s3_cmd += ("-segment_time", str(self.segment_size))
            s3_cmd += ("-segment_format", self.segment_format)
            s3_cmd += ("-reset_timestamps", "1")
            s3_cmd += (self.s3_archive_url / f"{self.segment_filename}.{self.segment_format}",)

            run(s3_cmd, check=True, stderr=DEVNULL)
            logger.info("archiver stopped")

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
