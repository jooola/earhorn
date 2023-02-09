import json
import logging
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from queue import Empty, Queue
from subprocess import PIPE, CalledProcessError, run
from threading import Event as ThreadEvent, Thread
from typing import List, Optional, Union

from pydantic import BaseModel, Field
from typing_extensions import Literal, Protocol, TypeAlias

from .prometheus import stream_silence, stream_status

logger = logging.getLogger(__name__)


def now():
    return datetime.now()


class Event(BaseModel):
    # pylint: disable=unnecessary-lambda
    when: datetime = Field(default_factory=lambda: now())


class SilenceEvent(Event):
    name = "silence"
    kind: Literal["start", "end"]
    seconds: Optional[Decimal]
    duration: Optional[Decimal]


class StatusEvent(Event):
    name = "status"
    kind: Literal["up", "down"]


AnyEvent: TypeAlias = Union[SilenceEvent, StatusEvent]


class Hook(Protocol):  # pylint: disable=too-few-public-methods
    def __call__(self, event: AnyEvent):
        pass


class HookError(Exception):
    """
    An error occurred during the hook execution.
    """


class FileHook:  # pylint: disable=too-few-public-methods
    filepath: Path
    log_stderr: bool

    def __init__(self, filepath: str, log_stderr: bool = False) -> None:
        self.filepath = Path(filepath)
        if not self.filepath.is_file():
            raise ValueError(f"hook '{self.filepath}' is not a file!")
        self.log_stderr = log_stderr

    def __call__(self, event: AnyEvent):
        try:
            # Improve once pydantic v2 is released
            # See https://github.com/pydantic/pydantic/discussions/4456
            event_dict = json.loads(event.json())

            env = {}
            for key, value in event_dict.items():
                if value is not None:
                    env[f"EVENT_{key.upper()}"] = str(value)

            cmd = run(str(self.filepath), env=env, check=True, stderr=PIPE, text=True)
            if self.log_stderr and cmd.stderr:
                logger.info(cmd.stderr)
        except CalledProcessError as exception:
            raise HookError(exception.stderr) from exception


class PrometheusHook:  # pylint: disable=too-few-public-methods
    def __call__(self, event: AnyEvent):
        if isinstance(event, StatusEvent):
            stream_status.state(event.kind)  # pylint: disable=no-member
        elif isinstance(event, SilenceEvent):
            state_map = {"start": "up", "end": "down"}
            stream_silence.state(state_map[event.kind])  # pylint: disable=no-member


class EventHandler(Thread):
    name = "event_handler"
    queue: Queue
    stop: ThreadEvent
    hooks: List[Hook] = []

    def __init__(
        self,
        queue: Queue,
        stop: ThreadEvent,
    ):
        Thread.__init__(self)
        self.queue = queue
        self.stop = stop

    def run(self):
        logger.info("starting event handler")

        while not self.stop.is_set() or not self.queue.empty():
            try:
                event = self.queue.get(timeout=2)
                logger.debug(event)
                for hook in self.hooks:
                    try:
                        hook(event)
                    except HookError as exception:
                        logger.exception(exception)

                self.queue.task_done()
            except Empty:
                pass

        logger.info("event handler stopped")
