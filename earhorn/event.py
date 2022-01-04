from datetime import datetime
from pathlib import Path
from queue import Empty, Queue
from subprocess import run
from threading import Event as ThreadEvent
from threading import Thread
from typing import Optional

from loguru import logger
from pydantic import BaseModel, Field


def now():
    return datetime.now()


class Event(BaseModel):
    # pylint: disable=unnecessary-lambda
    when: datetime = Field(default_factory=lambda: now())
    name: str


def handler(
    event: Event,
    hook: Optional[Path],
):
    logger.debug(f"{event.name}: {event.json()}")
    if hook is not None:
        run((hook, event.json()), check=True)


class Handler(Thread):
    name = "handler"
    queue: Queue
    stop: ThreadEvent
    hook: Optional[Path] = None

    def __init__(
        self,
        queue: Queue,
        stop: ThreadEvent,
        hook: Optional[str],
    ):
        Thread.__init__(self)
        self.queue = queue
        self.stop = stop

        if hook is not None:
            self.hook = Path(hook)
            if not self.hook.is_file():
                raise ValueError(f"hook '{self.hook}' is not a file!")

    def run(self):
        logger.info("starting event handler")

        while not self.stop.is_set():
            try:
                event = self.queue.get(timeout=5)
                handler(event, self.hook)
                self.queue.task_done()
            except Empty:
                pass

        logger.info("stopped event handler")
