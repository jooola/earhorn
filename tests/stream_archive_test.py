from pathlib import Path
from shutil import rmtree
from unittest.mock import MagicMock, call, patch

from earhorn.stream_archive import ArchiveHandler, LocalArchiveStorage


def test_local_archive_storage_ingest_segment(tmp_path: Path):
    tmp_segment = tmp_path / "somefile.txt"
    tmp_segment.write_text("test")

    segment_filepath = tmp_path / "somedir/anotherone/thesamefile.txt"

    storage = LocalArchiveStorage(str(tmp_path))
    storage.ingest_segment(tmp_segment, segment_filepath)

    assert (tmp_path / segment_filepath).is_file()
    assert (tmp_path / segment_filepath).read_text() == "test"


SEGMENTS_RAW = """
segment.2022-06-13-15-31-37.ogg,0.000000,4.993741
segment.2022-06-13-15-31-42.ogg,5.003900,10.001995
segment.2022-06-13-15-31-47.ogg,10.001995,15.000091
segment.2022-06-13-15-31-52.ogg,15.000091,20.002540
segment.2022-06-13-15-31-57.ogg,20.002540,21.186757
""".lstrip()


def test_archive_handler_wait_for_segments(tmp_path: Path):
    with patch("earhorn.stream_archive._mkfifo") as mkfifo_mock:
        mkfifo_mock.side_effect = lambda x: print(f"mocked fifo at {x}")

        storage = LocalArchiveStorage(str(tmp_path))
        storage.ingest_segment = MagicMock()  # type: ignore

        handler = ArchiveHandler(storage)
        handler.tmp_segment_list.write_text(SEGMENTS_RAW)

        handler.wait_for_segments()

        storage.ingest_segment.assert_has_calls(
            [
                call(
                    handler.tmp_dir / "segment.2022-06-13-15-31-37.ogg",
                    Path("2022/06/13/153137.ogg"),
                ),
                call(
                    handler.tmp_dir / "segment.2022-06-13-15-31-42.ogg",
                    Path("2022/06/13/153142.ogg"),
                ),
                call(
                    handler.tmp_dir / "segment.2022-06-13-15-31-47.ogg",
                    Path("2022/06/13/153147.ogg"),
                ),
                call(
                    handler.tmp_dir / "segment.2022-06-13-15-31-52.ogg",
                    Path("2022/06/13/153152.ogg"),
                ),
                call(
                    handler.tmp_dir / "segment.2022-06-13-15-31-57.ogg",
                    Path("2022/06/13/153157.ogg"),
                ),
            ]
        )

        rmtree(handler.tmp_dir)
