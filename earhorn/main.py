from pathlib import Path
from queue import Queue
from signal import SIGINT, SIGTERM, signal
from threading import Event as ThreadEvent
from threading import Thread
from typing import List, Optional

import click
from loguru import logger
from prometheus_client import start_http_server

from .archive import TIMESTAMP_FORMAT, Archiver
from .check import check_stream
from .event import FileHook, Handler, PrometheusHook
from .silence import SilenceListener


# pylint: disable=too-many-arguments,too-many-locals
@click.command(context_settings={"max_content_width": 120})
@click.option(
    "--hook",
    envvar="HOOK",
    help="Hook to run to handle events.",
    type=click.Path(),
)
@click.option(
    "--prometheus",
    envvar="PROMETHEUS",
    help="Enable prometheus metrics.",
    is_flag=True,
)
@click.option(
    "--prometheus-listen-port",
    envvar="PROMETHEUS_LISTEN_PORT",
    help="Listen port for the prometheus metrics server.",
    default=9950,
    show_default=True,
)
@click.option(
    "--archive-path",
    envvar="ARCHIVE_PATH",
    help="Path to the archive directory.",
    type=click.Path(),
)
@click.option(
    "--archive-segment-size",
    envvar="ARCHIVE_SEGMENT_SIZE",
    help="Archive segment size in seconds.",
    default=3600,
    show_default=True,
)
@click.option(
    "--archive-segment-filename",
    envvar="ARCHIVE_SEGMENT_FILENAME",
    help="Archive segment filename (without extension).",
    default=f"archive-{TIMESTAMP_FORMAT}",
    show_default=True,
)
@click.option(
    "--archive-segment-format",
    envvar="ARCHIVE_SEGMENT_FORMAT",
    help="Archive segment format.",
    default="ogg",
    show_default=True,
)
@click.argument(
    "url",
    envvar="URL",
)
def cli(
    url: str,
    hook: Optional[str],
    prometheus: bool,
    prometheus_listen_port: int,
    archive_path: Optional[str],
    archive_segment_size: int,
    archive_segment_filename: str,
    archive_segment_format: str,
):
    """
    URL of the stream.
    """
    stop_event = ThreadEvent()

    def stop_handler(_signum, _frame):
        logger.info("stopping...")
        stop_event.set()

    signal(SIGINT, stop_handler)
    signal(SIGTERM, stop_handler)

    # Setup event handler before doing any checks
    event_queue: Queue = Queue()

    handler = Handler(event_queue, stop_event)
    if hook is not None:
        handler.hooks.append(FileHook(hook))

    if prometheus:
        logger.info("starting prometheus server")
        start_http_server(prometheus_listen_port)
        handler.hooks.append(PrometheusHook())

    handler.start()

    while not stop_event.is_set():
        threads: List[Thread] = []

        # Check the stream until it is available
        check_stream(event_queue, stop_event, url)

        silence_listener = SilenceListener(event_queue, url)
        silence_listener.start()
        threads.append(silence_listener)

        if archive_path is not None:
            archiver = Archiver(
                url,
                Path(archive_path),
                archive_segment_size,
                archive_segment_filename,
                archive_segment_format,
            )
            archiver.start()
            threads.append(archiver)

        for thread in threads:
            thread.join()
