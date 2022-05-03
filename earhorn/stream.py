from os import getenv
from queue import Queue
from subprocess import DEVNULL, PIPE, Popen
from threading import Thread
from typing import Iterable, List

from loguru import logger
from typing_extensions import Protocol

FFMPEG = getenv("FFMPEG_PATH", "ffmpeg")


class StreamListenerHandler(Protocol):
    def ffmpeg_output(self) -> Iterable[str]:
        pass

    def process_handler(self, threads: List[Thread], process: Popen):
        pass


# pylint: disable=too-few-public-methods
class StreamListener:
    event_queue: Queue
    stream_url: str

    handlers: List[StreamListenerHandler] = []

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        stream_url: str,
        handlers: List[StreamListenerHandler],
    ):
        self.stream_url = stream_url

        if len(handlers) == 0:
            raise ValueError("stream listener requires at least one handler")
        self.handlers = handlers

    def run(self):
        logger.info("starting stream listener")

        cmd = [
            *(FFMPEG, "-hide_banner", "-nostats"),
            *("-re", "-vn", "-i", self.stream_url),
        ]

        for handler in self.handlers:
            cmd.extend(["-map", "0"] + handler.ffmpeg_output())

        logger.debug(f"running {cmd}")

        threads: List[Thread] = []
        with Popen(
            cmd,
            bufsize=1,
            stdout=DEVNULL,
            stderr=PIPE,
            text=True,
        ) as process:
            for handler in self.handlers:
                handler.process_handler(threads, process)
            process.wait()

        for thread in threads:
            thread.join()

        logger.info("stream listener stopped")
