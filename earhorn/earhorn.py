from pathlib import Path
from threading import Thread
from typing import List, Optional

from loguru import logger

from .archive import Archiver
from .silence import SilenceListener


# pylint: disable=too-many-arguments
def listen(
    url: str,
    silence_hook: Optional[str],
    archive_path: Optional[str],
    archive_segment_size: int,
    archive_segment_filename: str,
    archive_segment_format: str,
):

    threads: List[Thread] = []
    if silence_hook is not None:
        silence_listener = SilenceListener(url, Path(silence_hook))
        silence_listener.start()
        threads.append(silence_listener)

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

    if len(threads) == 0:
        logger.warning("nothing to do, exiting...")
    else:
        for thread in threads:
            thread.join()
