from pathlib import Path
from subprocess import DEVNULL, run
from threading import Thread
from typing import Optional

from loguru import logger

from ._ffmpeg import FFMPEG
import os, shutil
import boto3
import csv
from botocore.exceptions import ClientError

TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"

def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        return False
    return True


def get_files_and_upload(segment_list_file, filepath):
    final_content = []
    with open(segment_list_file, "r+") as csv_file:
        file_content = csv.reader(csv_file, delimiter=",")        
        for line in file_content:
            final_content.append(line[0])
        csv_file.truncate(0)
        similar_files  = []
        chosen_files_in_directory = os.listdir(filepath)

        for files in final_content:
            if files in chosen_files_in_directory:
                similar_files.append(files)
                final_file = str(filepath +"/"+ files)
                upload_file(final_file, os.getenv("AWS_STORAGE_BUCKET_NAME"))

        for filename in os.listdir(filepath):
            if filename in similar_files:
                file_to_be_removed = filepath +"/"+filename
                os.remove(file_to_be_removed)
    return "Files have been uploaded successfully"


class Archiver(Thread):
    name = "archiver"
    url: str
    path: Path
    segment_size: int
    segment_filename: str
    segment_format: str
    segment_format_options: Optional[str]
    copy_stream: bool
    s3_archive: bool


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
        s3_archive: bool
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
        self.s3_archive = s3_archive

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

        if self.s3_archive:
            cmd += ("-segment_list", "earhorn_segments.csv")
        
        cmd += (self.path / f"{self.segment_filename}.{self.segment_format}",)

        run(cmd, check=True, stderr=DEVNULL)
        logger.info("archiver stopped")
