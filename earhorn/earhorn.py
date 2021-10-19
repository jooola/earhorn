from pathlib import Path
from threading import Thread
from typing import List, Optional

from .archive import Archiver


# pylint: disable=too-many-arguments
def listen(
    url: str,
    archive_path: Optional[Path],
    archive_segment_size: int,
    archive_segment_filename: str,
    archive_segment_format: str,
):

    threads: List[Thread] = []
    if archive_path is not None:
        archiver = Archiver(
            url,
            Path(archive_path),
            archive_segment_size,
            archive_segment_filename,
            archive_segment_format,
        )
        archiver.start()
        threads.append(archiver)

    for thread in threads:
        thread.join()
