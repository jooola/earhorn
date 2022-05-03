from queue import Queue
from threading import Event as ThreadEvent
from time import sleep

import httpx
from loguru import logger

from .event import SilenceEvent, StatusEvent


def check_stream(
    event_queue: Queue,
    stop: ThreadEvent,
    url: str,
):
    """
    Check the stream until it is available.
    """
    while not stop.is_set():
        try:
            with httpx.stream("GET", url) as response:
                response.raise_for_status()
                event_queue.put(StatusEvent(kind="up"))
                event_queue.put(SilenceEvent(kind="end", seconds=0.0))
                return

        except (httpx.ConnectError, httpx.HTTPStatusError) as error:
            logger.error(f"could not stream from '{url}'")
            logger.debug(error)
            event_queue.put(StatusEvent(kind="down"))
            sleep(5)
