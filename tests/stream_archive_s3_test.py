from pathlib import Path

import boto3
from moto import mock_s3  # type: ignore

from earhorn.stream_archive_s3 import S3ArchiveStorage


@mock_s3
def test_s3_archive_storage_ingest_segment(tmp_path: Path):
    tmp_segment = tmp_path / "somefile.txt"
    tmp_segment.write_text("test")

    segment_filepath = tmp_path / "somedir/anotherone/thesamefile.txt"

    # Create fake bucket
    bucket_name = "my-bucket"
    conn = boto3.resource("s3")
    conn.create_bucket(Bucket=bucket_name)

    storage = S3ArchiveStorage(f"s3://{bucket_name}")
    storage.ingest_segment(tmp_segment, segment_filepath)

    assert (
        conn.Object(bucket_name, str(segment_filepath))
        .get()["Body"]
        .read()
        .decode("utf-8")
        == "test"
    )
