import logging
from os import getenv
from queue import Queue
from subprocess import DEVNULL, PIPE, Popen
from threading import Event as ThreadEvent, Thread
from time import sleep
from typing import List, Optional

import httpx
from typing_extensions import Protocol

from .event import SilenceEvent, StatusEvent

logger = logging.getLogger(__name__)

FFMPEG = getenv("FFMPEG_PATH", "ffmpeg")


class StreamListenerHandler(Protocol):
    def ffmpeg_output(self) -> List[str]:
        pass

    def process_handler(self, threads: List[Thread], process: Popen):
        pass


# pylint: disable=too-few-public-methods
class StreamListener:
    stop: ThreadEvent
    event_queue: Queue
    stream_url: str

    _handlers: List[StreamListenerHandler] = []
    _client: httpx.Client
    _process: Optional[Popen]

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        stop: ThreadEvent,
        event_queue: Queue,
        stream_url: str,
        handlers: List[StreamListenerHandler],
    ):
        self.stop = stop
        self.event_queue = event_queue
        self.stream_url = stream_url

        if len(handlers) == 0:
            raise ValueError("stream listener requires at least one handler")

        self._handlers = handlers
        self._client = httpx.Client()
        self._process = None

    def _ffmpeg_command(self):
        command = [
            *(FFMPEG, "-hide_banner", "-nostats"),
            *("-re", "-vn", "-i", self.stream_url),
        ]

        for handler in self._handlers:
            command.extend(["-map", "0"] + handler.ffmpeg_output())

        return command

    def check_stream(self):
        """
        Check the stream until it is available.
        """
        while not self.stop.is_set():
            try:
                with self._client.stream("GET", self.stream_url) as response:
                    response.raise_for_status()
                    self.event_queue.put(StatusEvent(kind="up"))
                    self.event_queue.put(SilenceEvent(kind="end", seconds=0.0))
                    return

            except (
                httpx.HTTPStatusError,
                httpx.NetworkError,
                httpx.TimeoutException,
                httpx.TransportError,
            ) as error:
                logger.error(f"could not stream from '{self.stream_url}'")
                logger.debug(error)
                self.event_queue.put(StatusEvent(kind="down"))
                sleep(5)

    def run_forever(self):
        while not self.stop.is_set():
            self.check_stream()
            self.listen()

        self._client.close()

    def listen(self):
        logger.info("starting stream listener")

        # Run setup tasks before starting to listen for the stream
        for handler in self._handlers:
            if hasattr(handler, "before_listen_start"):
                logger.info(f"preparing {handler.__class__.__name__} ")
                handler.before_listen_start()

        command = self._ffmpeg_command()
        logger.debug(f"running ffmpeg command '{' '.join(command)}'")

        threads: List[Thread] = []
        with Popen(
            command,
            bufsize=1,
            stdout=DEVNULL,
            stderr=PIPE,
            text=True,
            encoding="utf-8",
            errors="backslashreplace",
        ) as process:
            self._process = process

            for handler in self._handlers:
                handler.process_handler(threads, self._process)
            exit_code = self._process.wait()

        logger.info(f"ffmpeg command exited with {exit_code}")

        for thread in threads:
            thread.join()

        logger.info("stream listener stopped")

    def stop_listener(self):
        if self._process is not None:
            self._process.terminate()
