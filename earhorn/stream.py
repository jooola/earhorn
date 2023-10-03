import logging
from abc import ABC, abstractmethod
from decimal import Decimal
from os import getenv
from queue import Queue
from subprocess import DEVNULL, PIPE, Popen
from threading import Event as ThreadEvent, Thread
from time import sleep
from typing import Optional

import httpx

from .event import SilenceEvent, StatusEvent

logger = logging.getLogger(__name__)

FFMPEG = getenv("FFMPEG_PATH", "ffmpeg")


class StreamListenerHandler(ABC, Thread):
    name: str
    queue: Queue

    @abstractmethod
    def ffmpeg_output(self) -> list[str]:
        pass


# pylint: disable=too-few-public-methods
class StreamListener:
    name = "stream_listener"
    stop: ThreadEvent
    event_queue: Queue
    stream_url: str

    _handlers: list[StreamListenerHandler] = []
    _client: httpx.Client
    _process: Optional[Popen]

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        stop: ThreadEvent,
        event_queue: Queue,
        stream_url: str,
        handlers: list[StreamListenerHandler],
    ):
        self.stop = stop
        self.event_queue = event_queue
        self.stream_url = stream_url

        if len(handlers) == 0:
            raise ValueError("stream listener requires at least one handler")

        self._handlers = handlers
        self._client = httpx.Client()
        self._process = None

        for handler in self._handlers:
            logger.debug("starting %s", handler.name)
            handler.start()

    def _ffmpeg_command(self):
        command = [
            *(FFMPEG, "-hide_banner", "-nostats"),
            *("-loglevel", "40"),  # Verbose
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
                    self.event_queue.put(
                        SilenceEvent(kind="end", seconds=Decimal("0.0"))
                    )
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

        for handler in self._handlers:
            logger.debug("joining %s", handler.name)
            handler.join(timeout=3.0)

    def listen(self):
        logger.info("starting %s", self.name)

        command = self._ffmpeg_command()
        logger.debug(f"running ffmpeg command '{' '.join(command)}'")

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

            assert self._process.stderr is not None
            for line in iter(self._process.stderr.readline, ""):
                line = line.rstrip()
                logger.debug(line)
                for handler in self._handlers:
                    handler.queue.put(line)

            exit_code = self._process.wait()

        logger.info(f"ffmpeg command exited with {exit_code}")

        logger.info("%s stopped", self.name)

    def stop_listener(self):
        if self._process is not None:
            self._process.terminate()
