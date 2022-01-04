from pathlib import Path
from queue import Queue
from signal import SIGINT, SIGTERM, signal
from threading import Event as ThreadEvent
from threading import Thread
from typing import List, Optional

from loguru import logger

from .archive import Archiver
from .check import check_stream
from .event import Event, Handler
from .silence import SilenceListener


# pylint: disable=too-many-arguments
def run(
    url: str,
    hook: Optional[str],
    archive_path: Optional[str],
    archive_segment_size: int,
    archive_segment_filename: str,
    archive_segment_format: str,
):
    stop_event = ThreadEvent()

    def stop_handler(_signum, _frame):
        logger.info("stopping...")
        stop_event.set()

    signal(SIGINT, stop_handler)
    signal(SIGTERM, stop_handler)

    # Setup event handler before doing any checks
    event_queue: Queue[Event] = Queue()
    handler = Handler(event_queue, stop_event, hook)
    handler.start()

    while not stop_event.is_set():
        threads: List[Thread] = []

        # Check the stream until it is available
        check_stream(event_queue, stop_event, url)

        silence_listener = SilenceListener(event_queue, url)
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

        for thread in threads:
            thread.join()
