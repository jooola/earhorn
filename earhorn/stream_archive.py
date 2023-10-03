import logging
import re
from itertools import chain
from pathlib import Path
from queue import Empty, Queue
from shutil import move
from threading import Event as ThreadEvent
from typing import Optional

from typing_extensions import Protocol

from .prometheus import archive_errors, archive_segments
from .stream import StreamListenerHandler

logger = logging.getLogger(__name__)

DEFAULT_ARCHIVE_SEGMENT_SIZE: int = 3600
DEFAULT_ARCHIVE_SEGMENT_FORMAT: str = "ogg"

DEFAULT_ARCHIVE_SEGMENT_FILEPATH: str = (
    "{year}/{month}/{day}/{hour}{minute}{second}.{format}"
)

SEGMENT_STARTED_RE = re.compile(
    r"\[segment @ .*\] segment:'(.*)' starts with packet .*",
)
SEGMENT_ENDED_RE = re.compile(
    r"\[segment @ .*\] segment:'(.*)' count:\d+ ended",
)


def parse_segment_line(regex: re.Pattern, line: str) -> Optional[Path]:
    line = line.strip()
    match = regex.search(line)
    if match is None:
        return None

    return Path(match.group(1))


class IngestSegmentError(Exception):
    """An error occurred while ingesting a segment"""


class InvalidSegmentFilename(IngestSegmentError):
    """Invalid segment filename"""


# pylint: disable=too-few-public-methods
class ArchiveStorage(Protocol):
    def ingest_segment(self, segment: Path, segment_filepath: Path):
        ...


# pylint: disable=too-few-public-methods
class LocalArchiveStorage:
    path: Path

    def __init__(self, path: str) -> None:
        self.path = Path(path)
        if not self.path.is_dir():
            raise ValueError(f"archive path '{path}' is not a directory!")

    def ingest_segment(self, segment: Path, segment_filepath: Path):
        segment_fullpath = self.path / segment_filepath

        try:
            logger.debug(f"moving segment to {segment_fullpath}")
            segment_fullpath.parent.mkdir(parents=True, exist_ok=True)
            move(segment, segment_fullpath)
        except OSError as exception:
            raise IngestSegmentError(exception) from exception


# pylint: disable=too-many-instance-attributes
class ArchiveHandler(StreamListenerHandler):
    name = "archive_handler"
    stop: ThreadEvent
    queue: Queue

    SEGMENTS_DIR: str = "incoming"
    SEGMENTS_PENDING_DIR: str = "pending"
    SEGMENT_PREFIX: str = "segment"
    SEGMENT_STRFTIME: str = "%Y-%m-%d-%H-%M-%S"

    storage: ArchiveStorage

    segment_filepath: str
    segment_size: int
    segment_format: str
    segment_format_options: Optional[str]
    copy_stream: bool

    segments_pending_queue: set[Path]

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        stop: ThreadEvent,
        storage: ArchiveStorage,
        segment_filepath: str = DEFAULT_ARCHIVE_SEGMENT_FILEPATH,
        segment_size: int = DEFAULT_ARCHIVE_SEGMENT_SIZE,
        segment_format: str = DEFAULT_ARCHIVE_SEGMENT_FORMAT,
        segment_format_options: Optional[str] = None,
        copy_stream: bool = False,
    ):
        super().__init__()
        self.stop = stop
        self.queue = Queue()

        self.storage = storage

        self.segment_filepath = segment_filepath
        self.segment_size = segment_size
        self.segment_format = segment_format
        self.segment_format_options = segment_format_options
        self.copy_stream = copy_stream

        self.segments_dir = Path(self.SEGMENTS_DIR)
        self.segments_pending_dir = Path(self.SEGMENTS_PENDING_DIR)

        self.segments_dir.mkdir(exist_ok=True)
        self.segments_pending_dir.mkdir(exist_ok=True)

        self.segments_pending_queue = set()

    def _tmp_segment_filename(self) -> Path:
        return Path(
            ".".join(
                [
                    self.SEGMENT_PREFIX,
                    self.SEGMENT_STRFTIME,
                    self.segment_format,
                ]
            )
        )

    def _segment_filepath(self, segment: Path) -> Path:
        try:
            filename_parts = segment.name.split(".")
            datetime_str = filename_parts[1]
            datetime_parts = datetime_str.split("-")

            return Path(
                self.segment_filepath.format(
                    **{
                        "format": self.segment_format,
                        "year": datetime_parts[0],
                        "month": datetime_parts[1],
                        "day": datetime_parts[2],
                        "hour": datetime_parts[3],
                        "minute": datetime_parts[4],
                        "second": datetime_parts[5],
                    }
                )
            )
        except IndexError as error:
            raise InvalidSegmentFilename(
                f"found invalid segment filename {segment.name}"
            ) from error

    def ffmpeg_output(self):
        args = ["-map_metadata", "-1"]

        if self.copy_stream:
            logger.info("enabling stream copy")
            args += ("-c", "copy")

        args += (
            *("-f", "segment"),
            *("-strftime", "1"),
            *("-segment_time", str(self.segment_size)),
            *("-segment_format", self.segment_format),
        )

        if self.segment_format_options:
            args += ("-segment_format_options", self.segment_format_options)

        args += (
            *("-reset_timestamps", "1"),
            str(self.segments_dir / self._tmp_segment_filename()),
        )

        return args

    def gather_unmanaged_segments(self):
        for segment_incoming in chain(
            self.segments_dir.iterdir(),
            self.segments_pending_dir.iterdir(),
        ):
            self.accept_incoming_segment(segment_incoming)

    def accept_incoming_segment(self, segment_incoming: Path) -> Path:
        segment_pending = self.segments_pending_dir / segment_incoming.name

        if segment_incoming != segment_pending:
            logger.debug(f"moving {segment_incoming} to {segment_pending}")
            move(segment_incoming, segment_pending)

        self.segments_pending_queue.add(segment_pending)

        return segment_pending

    def _ingest_segment(self, segment: Path):
        with archive_errors.count_exceptions(IngestSegmentError):
            self.storage.ingest_segment(
                segment,
                self._segment_filepath(segment),
            )
            archive_segments.labels(state="ingested").inc()

    def ingest_pending_segments(self):
        while self.segments_pending_queue:
            segment = self.segments_pending_queue.pop()

            try:
                self._ingest_segment(segment)
            except IngestSegmentError as exception:
                self.segments_pending_queue.add(segment)

                logger.error(exception)

                # Go try to ingest segments from incoming, pending can wait
                break

    def run(self):
        logger.info("starting %s", self.name)

        # Ingest pending segments before starting
        self.gather_unmanaged_segments()
        self.ingest_pending_segments()

        while not self.stop.is_set() or not self.queue.empty():
            try:
                line = self.queue.get(timeout=1.0)
            except Empty:
                continue

            segment_started = parse_segment_line(SEGMENT_STARTED_RE, line)
            if segment_started is not None:
                logger.info("segment started %s", segment_started)
                self.queue.task_done()
                continue

            segment_ended = parse_segment_line(SEGMENT_ENDED_RE, line)
            if segment_ended is None:
                self.queue.task_done()
                continue

            logger.info("segment ended %s", segment_ended)

            try:
                self.accept_incoming_segment(segment_ended)
                archive_segments.labels(state="incoming").inc()
                self.queue.task_done()

                self.ingest_pending_segments()
            except InvalidSegmentFilename as exception:
                logger.error(exception)
                continue
            except IngestSegmentError as exception:
                logger.error(exception)
                archive_segments.labels(state="pending").inc()

        self.gather_unmanaged_segments()
        self.ingest_pending_segments()
        logger.info("%s stopped", self.name)
