import re
from datetime import datetime
from math import isclose
from pathlib import Path
from subprocess import DEVNULL, PIPE, Popen, run
from threading import Thread
from typing import NamedTuple, Optional

from loguru import logger

NOISE = 0.001

SILENCE_DETECT_RE = re.compile(
    r"\[silencedetect.*\] silence_(start|end): (\d+(?:\.\d+)?)(?: \| silence_duration: (\d+\.\d+))?"
)


class SilenceEvent(NamedTuple):
    when: datetime
    kind: str
    seconds: float
    duration: Optional[float]


def now():
    return datetime.now()


def parse_silence_detect(line: str) -> Optional[SilenceEvent]:
    match = SILENCE_DETECT_RE.search(line)
    if match is None:
        return None

    return SilenceEvent(
        now(),
        match.group(1),
        float(match.group(2)),
        float(match.group(3)) if match.group(3) else None,
    )


def validate_silence_duration(
    start: SilenceEvent,
    end: SilenceEvent,
) -> bool:
    if end.duration is None:
        return False
    duration_ffmpeg = end.duration
    duration_ours = end.seconds - start.seconds
    is_valid = isclose(duration_ffmpeg, duration_ours, abs_tol=0.01)
    if not is_valid:
        logger.error(
            f"computed duration '{duration_ours}'"
            f"differs from ffmpeg duration {duration_ffmpeg}"
        )
    return is_valid


def handle_silence_event(hook: Path, event: SilenceEvent):
    run((hook, event.kind, event.when.isoformat()), check=True)


class SilenceListener(Thread):
    name = "silence_listener"
    url: str
    hook: Path

    def __init__(self, url, hook):
        Thread.__init__(self)
        self.url = url

        if not hook.is_file():
            raise ValueError(f"hook '{hook}' is not a file!")
        self.hook = hook

    def run(self):
        logger.info("starting silence listener")

        with Popen(
            (
                *("ffmpeg", "-hide_banner", "-nostats"),
                *("-re", "-i", self.url),
                "-vn",  # Drop video
                *("-af", f"silencedetect=noise={NOISE}"),
                *("-f", "null", "/dev/null"),
            ),
            bufsize=1,
            stdout=DEVNULL,
            stderr=PIPE,
            text=True,
        ) as process:
            logger.debug("starting to parse stdout")

            previous = None
            for line in process.stderr:
                event = parse_silence_detect(line)
                if event is None:
                    continue

                if event.kind == "end":
                    validate_silence_duration(previous, event)

                logger.info(f"silence {event.kind}: {event.when}")
                handle_silence_event(self.hook, event)
                previous = event
