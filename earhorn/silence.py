import re
from math import isclose
from queue import Queue
from subprocess import DEVNULL, PIPE, Popen
from threading import Thread
from typing import Optional

from loguru import logger

from ._ffmpeg import FFMPEG
from .event import SilenceEvent

NOISE = 0.001

SILENCE_DETECT_RE = re.compile(
    r"\[silencedetect.*\] silence_(start|end): (\d+(?:\.\d+)?)(?: \| silence_duration: (\d+\.\d+))?"
)


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


def silence_listener(event_queue: Queue, url: str):
    with Popen(
        (
            *(FFMPEG, "-hide_banner", "-nostats"),
            *("-re", "-i", url),
            "-vn",  # Drop video
            *("-af", f"silencedetect=noise={NOISE}"),
            *("-f", "null", "/dev/null"),
        ),
        bufsize=1,
        stdout=DEVNULL,
        stderr=PIPE,
        text=True,
    ) as process:
        previous = None

        logger.debug("starting to parse stdout")
        for line in process.stderr:  # type: ignore
            event = parse_silence_detect(line)
            if event is None:
                continue

            if event.kind == "end" and previous is not None:
                validate_silence_duration(previous, event)

            logger.info(f"silence {event.kind}: {event.when}")
            event_queue.put(event)
            previous = event


class SilenceListener(Thread):
    name = "silence_listener"
    event_queue: Queue
    url: str

    def __init__(self, event_queue, url):
        Thread.__init__(self)
        self.event_queue = event_queue
        self.url = url

    def run(self):
        logger.info("starting silence listener")
        silence_listener(self.event_queue, self.url)
        logger.info("silence listener stopped")
