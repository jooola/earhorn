import re
from decimal import Decimal
from queue import Queue
from subprocess import Popen
from threading import Thread
from typing import List, Optional

from loguru import logger

from .event import SilenceEvent

SILENCE_DETECT_RE = re.compile(
    r"\[silencedetect.*\] silence_(start|end): (\d+(?:\.\d+)?)(?: \| silence_duration: (\d+\.\d+))?"
)

# https://ffmpeg.org/ffmpeg-filters.html#silencedetect
DEFAULT_SILENCE_DETECT_NOISE: str = "-60dB"
# https://ffmpeg.org/ffmpeg-utils.html#time-duration-syntax
DEFAULT_SILENCE_DETECT_DURATION: str = "2.0"


def parse_silence_detect(line: str) -> Optional[SilenceEvent]:
    line = line.strip()
    match = SILENCE_DETECT_RE.search(line)
    if match is None:
        return None

    logger.debug(line)

    return SilenceEvent(
        kind=match.group(1),
        seconds=Decimal(match.group(2)),
        duration=Decimal(match.group(3)) if match.group(3) else None,
    )


# pylint: disable=too-few-public-methods
class SilenceHandler:
    event_queue: Queue

    noise: str
    duration: str

    def __init__(
        self,
        event_queue: Queue,
        noise: str = DEFAULT_SILENCE_DETECT_NOISE,
        duration: str = DEFAULT_SILENCE_DETECT_DURATION,
    ):
        self.event_queue = event_queue
        self.noise = noise
        self.duration = duration

    def ffmpeg_output(self):
        return [
            *("-af", f"silencedetect=noise={self.noise}:d={self.duration}"),
            *("-f", "null", "/dev/null"),
        ]

    def parse_process_output(self, process: Popen):
        logger.debug("starting to parse stdout")
        for line in process.stderr:  # type: ignore
            event = parse_silence_detect(line)
            if event is None:
                continue

            logger.info(f"silence {event.kind}: {event.when}")
            self.event_queue.put(event)

    def process_handler(self, threads: List[Thread], process: Popen):
        thread = Thread(target=self.parse_process_output, args=(process,))
        thread.start()
        threads.append(thread)
