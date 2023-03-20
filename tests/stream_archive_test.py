from pathlib import Path
from threading import Event as ThreadEvent
from unittest.mock import MagicMock, Mock, call, patch

import pytest

from earhorn.stream_archive import (
    ArchiveHandler,
    InvalidSegmentFilename,
    LocalArchiveStorage,
)


def test_archive_handler_segment_filepath(tmp_path: Path):
    handler = ArchiveHandler(None, None)  # type: ignore
    # pylint: disable=protected-access
    assert handler._segment_filepath(tmp_path / "segment.2022-06-13-15-31-37.ogg")


@pytest.mark.parametrize(
    "filename",
    [
        "2022-06-13-15-31-37.ogg",  # no prefix
        "segment.06-13-15-31-37.ogg",  # no year
    ],
)
def test_archive_handler_segment_filepath_invalid(tmp_path: Path, filename: str):
    handler = ArchiveHandler(None, None)  # type: ignore
    with pytest.raises(InvalidSegmentFilename):
        # pylint: disable=protected-access
        handler._segment_filepath(tmp_path / filename)


def test_local_archive_storage_ingest_segment(tmp_path: Path):
    tmp_segment = tmp_path / "somefile.txt"
    tmp_segment.write_text("test")

    segment_filepath = tmp_path / "somedir/anotherone/thesamefile.txt"

    storage = LocalArchiveStorage(str(tmp_path))
    storage.ingest_segment(tmp_segment, segment_filepath)

    assert (tmp_path / segment_filepath).is_file()
    assert (tmp_path / segment_filepath).read_text() == "test"


SEGMENTS_RAW = """
[segment @ 0x56163fd63b40] Selected stream id:0 type:audio
[segment @ 0x56163fd63b40] Opening 'incoming/segment.2023-03-20-16-18-54.ogg' for writing
[segment @ 0x56163fd63b40] segment:'incoming/segment.2023-03-20-16-18-54.ogg' starts with packet stream:0 pts:896 pts_time:0.0203175 frame:0
[segment @ 0x56163fd63b40] segment:'incoming/segment.2023-03-20-16-18-54.ogg' count:0 ended
[AVIOContext @ 0x56163fe18540] Statistics: 0 seeks, 1 writeouts
[segment @ 0x56163fd63b40] Opening 'incoming/segment.2023-03-20-16-18-59.ogg' for writing
[segment @ 0x56163fd63b40] segment:'incoming/segment.2023-03-20-16-18-59.ogg' starts with packet stream:0 pts:220864 pts_time:5.00825 frame:217
[segment @ 0x56163fd63b40] segment:'incoming/segment.2023-03-20-16-18-59.ogg' count:1 ended
[AVIOContext @ 0x56163fe15b80] Statistics: 0 seeks, 1 writeouts
[segment @ 0x56163fd63b40] Opening 'incoming/segment.2023-03-20-16-19-04.ogg' for writing
[segment @ 0x56163fd63b40] segment:'incoming/segment.2023-03-20-16-19-04.ogg' starts with packet stream:0 pts:441024 pts_time:10.0005 frame:432
[segment @ 0x56163fd63b40] segment:'incoming/segment.2023-03-20-16-19-04.ogg' count:2 ended
[AVIOContext @ 0x56163fe0f7c0] Statistics: 0 seeks, 1 writeouts
[segment @ 0x56163fd63b40] Opening 'incoming/segment.2023-03-20-16-19-09.ogg' for writing
[segment @ 0x56163fd63b40] segment:'incoming/segment.2023-03-20-16-19-09.ogg' starts with packet stream:0 pts:662208 pts_time:15.0161 frame:648
[segment @ 0x56163fd63b40] segment:'incoming/segment.2023-03-20-16-19-09.ogg' count:3 ended
[AVIOContext @ 0x56163fe82640] Statistics: 0 seeks, 1 writeouts
[segment @ 0x56163fd63b40] Opening 'incoming/segment.2023-03-20-16-19-14.ogg' for writing
[segment @ 0x56163fd63b40] segment:'incoming/segment.2023-03-20-16-19-14.ogg' starts with packet stream:0 pts:882368 pts_time:20.0083 frame:863
[segment @ 0x56163fd63b40] segment:'incoming/segment.2023-03-20-16-19-14.ogg' count:4 ended
[AVIOContext @ 0x56163fe10f00] Statistics: 0 seeks, 1 writeouts
[segment @ 0x56163fd63b40] Opening 'incoming/segment.2023-03-20-16-19-19.ogg' for writing
[segment @ 0x56163fd63b40] segment:'incoming/segment.2023-03-20-16-19-19.ogg' starts with packet stream:0 pts:1102528 pts_time:25.0006 frame:1078
[segment @ 0x56163fd63b40] segment:'incoming/segment.2023-03-20-16-19-19.ogg' count:5 ended
[AVIOContext @ 0x56163fe10d80] Statistics: 0 seeks, 1 writeouts
[segment @ 0x56163fd63b40] Opening 'incoming/segment.2023-03-20-16-19-24.ogg' for writing
[segment @ 0x56163fd63b40] segment:'incoming/segment.2023-03-20-16-19-24.ogg' starts with packet stream:0 pts:1323712 pts_time:30.0161 frame:1294
""".strip()


@patch("earhorn.stream_archive.move")
def test_archive_handler(move_mock: Mock):
    stop_event = ThreadEvent()

    storage = MagicMock(spec=LocalArchiveStorage)
    handler = ArchiveHandler(stop_event, storage)

    for line in SEGMENTS_RAW.splitlines():
        handler.queue.put(line)
    stop_event.set()

    handler.run()

    move_mock.assert_has_calls(
        [
            call(
                Path("incoming/segment.2023-03-20-16-18-54.ogg"),
                Path("pending/segment.2023-03-20-16-18-54.ogg"),
            ),
            call(
                Path("incoming/segment.2023-03-20-16-18-59.ogg"),
                Path("pending/segment.2023-03-20-16-18-59.ogg"),
            ),
            call(
                Path("incoming/segment.2023-03-20-16-19-04.ogg"),
                Path("pending/segment.2023-03-20-16-19-04.ogg"),
            ),
            call(
                Path("incoming/segment.2023-03-20-16-19-09.ogg"),
                Path("pending/segment.2023-03-20-16-19-09.ogg"),
            ),
            call(
                Path("incoming/segment.2023-03-20-16-19-14.ogg"),
                Path("pending/segment.2023-03-20-16-19-14.ogg"),
            ),
            call(
                Path("incoming/segment.2023-03-20-16-19-19.ogg"),
                Path("pending/segment.2023-03-20-16-19-19.ogg"),
            ),
        ]
    )

    storage.ingest_segment.assert_has_calls(
        [
            call(
                Path("pending/segment.2023-03-20-16-18-54.ogg"),
                Path("2023/03/20/161854.ogg"),
            ),
            call(
                Path("pending/segment.2023-03-20-16-18-59.ogg"),
                Path("2023/03/20/161859.ogg"),
            ),
            call(
                Path("pending/segment.2023-03-20-16-19-04.ogg"),
                Path("2023/03/20/161904.ogg"),
            ),
            call(
                Path("pending/segment.2023-03-20-16-19-09.ogg"),
                Path("2023/03/20/161909.ogg"),
            ),
            call(
                Path("pending/segment.2023-03-20-16-19-14.ogg"),
                Path("2023/03/20/161914.ogg"),
            ),
            call(
                Path("pending/segment.2023-03-20-16-19-19.ogg"),
                Path("2023/03/20/161919.ogg"),
            ),
        ]
    )
