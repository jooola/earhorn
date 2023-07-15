import logging
import re
from decimal import Decimal
from queue import Empty, Queue
from threading import Event as ThreadEvent
from typing import Optional

from .event import SilenceEvent
from .stream import StreamListenerHandler

logger = logging.getLogger(__name__)

SILENCE_DETECT_RE = re.compile(
    r"\[silencedetect.*\] silence_(start|end): (\d+(?:\.\d+)?)(?: \| silence_duration: (\d+\.\d+))?"
)

# https://ffmpeg.org/ffmpeg-filters.html#silencedetect
DEFAULT_SILENCE_DETECT_RAW: str = "silencedetect=noise={noise}:d={duration}"
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
        kind=match.group(1),  # type: ignore[arg-type]
        seconds=Decimal(match.group(2)),
        duration=Decimal(match.group(3)) if match.group(3) else None,
    )


# pylint: disable=too-few-public-methods
class SilenceHandler(StreamListenerHandler):
    name = "silence_handler"
    stop: ThreadEvent
    queue: Queue

    event_queue: Queue

    noise: str
    duration: str
    raw: str

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        stop: ThreadEvent,
        event_queue: Queue,
        noise: str = DEFAULT_SILENCE_DETECT_NOISE,
        duration: str = DEFAULT_SILENCE_DETECT_DURATION,
        raw: str = DEFAULT_SILENCE_DETECT_RAW,
    ):
        super().__init__()
        self.stop = stop
        self.queue = Queue()

        self.event_queue = event_queue
        self.noise = noise
        self.duration = duration
        self.raw = raw

    def ffmpeg_output(self):
        return [
            *("-af", self.raw.format(noise=self.noise, duration=self.duration)),
            *("-f", "null", "/dev/null"),
        ]

    def run(self):
        logger.info("starting %s", self.name)

        # pylint: disable=duplicate-code
        while not self.stop.is_set() or not self.queue.empty():
            try:
                line = self.queue.get(timeout=1.0)
            except Empty:
                continue

            event = parse_silence_detect(line)
            if event is not None:
                logger.info(f"silence {event.kind}: {event.when}")
                self.event_queue.put(event)

            self.queue.task_done()

        logger.info("%s stopped", self.name)
