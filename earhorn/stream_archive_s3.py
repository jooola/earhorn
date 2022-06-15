import os
from pathlib import Path
from typing import Any

from boto3 import client
from botocore.exceptions import ClientError
from loguru import logger


# pylint: disable=too-few-public-methods
class S3ArchiveStorage:
    bucket: str
    _client: Any

    def __init__(self, url: str) -> None:
        self.bucket = url.split("//")[1]
        self._client = client(
            "s3",
            region_name=os.getenv("AWS_S3_REGION_NAME"),
            endpoint_url=os.getenv("AWS_S3_ENDPOINT_URL"),
        )

    def ingest_segment(self, tmp_segment: Path, segment_filepath: Path):
        logger.debug(f"uploading segment {tmp_segment} to s3://{self.bucket}")
        try:
            self._client.upload_file(
                str(tmp_segment),
                self.bucket,
                Key=str(segment_filepath),
            )
        except ClientError as exception:
            logger.error(f"could not upload {tmp_segment}: {exception}")
            return

        # Only remove if upload succeeded
        tmp_segment.unlink()
