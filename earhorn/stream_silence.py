import re
from math import isclose
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
DEFAULT_SILENCE_DETECT_DURATION: str = "2"


def parse_silence_detect(line: str) -> Optional[SilenceEvent]:
    match = SILENCE_DETECT_RE.search(line)
    if match is None:
        return None

    return SilenceEvent(
        kind=match.group(1),
        seconds=float(match.group(2)),
        duration=float(match.group(3)) if match.group(3) else None,
    )


def validate_silence_duration(
    start: SilenceEvent,
    end: Optional[SilenceEvent],
) -> Optional[bool]:
    if end is None:
        return None

    if end.duration is None or end.seconds is None or start.seconds is None:
        return False

    duration_ffmpeg = end.duration
    duration_ours = end.seconds - start.seconds
    is_valid = isclose(duration_ffmpeg, duration_ours, abs_tol=0.01)
    if not is_valid:
        logger.error(
            f"computed duration '{duration_ours}' "
            f"differs from ffmpeg duration '{duration_ffmpeg}'"
        )
    return is_valid


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
        previous = None

        logger.debug("starting to parse stdout")
        for line in process.stderr:  # type: ignore
            event = parse_silence_detect(line)
            if event is None:
                continue

            if event.kind == "end" and previous is not None:
                validate_silence_duration(previous, event)

            logger.info(f"silence {event.kind}: {event.when}")
            self.event_queue.put(event)
            previous = event

    def process_handler(self, threads: List[Thread], process: Popen):
        thread = Thread(target=self.parse_process_output, args=(process,))
        thread.start()
        threads.append(thread)
