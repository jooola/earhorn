from queue import Queue
from signal import SIGINT, SIGTERM, signal
from threading import Event as ThreadEvent
from typing import List, Optional

import click
from loguru import logger
from prometheus_client import start_http_server

from .event import EventHandler, FileHook, PrometheusHook
from .stats import StatsCollector
from .stream import StreamListener, StreamListenerHandler
from .stream_archive import (
    DEFAULT_ARCHIVE_SEGMENT_FILENAME,
    DEFAULT_ARCHIVE_SEGMENT_FORMAT,
    DEFAULT_ARCHIVE_SEGMENT_SIZE,
    ArchiveHandler,
)
from .stream_check import check_stream
from .stream_silence import (
    DEFAULT_SILENCE_DETECT_DURATION,
    DEFAULT_SILENCE_DETECT_NOISE,
    SilenceHandler,
)


# pylint: disable=too-many-arguments,too-many-locals
@click.command(context_settings={"max_content_width": 120})
@click.option(
    "--listen-port",
    envvar="LISTEN_PORT",
    help="Listen port for the prometheus metrics endpoint.",
    default=9950,
    show_default=True,
)
@click.option(
    "--hook",
    envvar="HOOK",
    help="Path to a custom script executed to handle stream state `events`.",
    type=click.Path(),
)
@click.option(
    "--stats-url",
    envvar="STATS_URL",
    help="URL to the icecast admin xml stats page.",
)
@click.option(
    "--stats-user",
    envvar="STATS_USER",
    help="Username for the icecast admin xml stats page.",
    default="admin",
    show_default=True,
)
@click.option(
    "--stats-password",
    envvar="STATS_PASSWORD",
    help="Password for the icecast admin xml stats page.",
)
@click.option(
    "--stream-url",
    envvar="STREAM_URL",
    help="URL to the icecast stream.",
)
@click.option(
    "--silence-detect-noise",
    envvar="SILENCE_DETECT_NOISE",
    help="Silence detect noise.",
    default=DEFAULT_SILENCE_DETECT_NOISE,
    show_default=True,
)
@click.option(
    "--silence-detect-duration",
    envvar="SILENCE_DETECT_DURATION",
    help="Silence detect duration.",
    default=DEFAULT_SILENCE_DETECT_DURATION,
    show_default=True,
)
@click.option(
    "--archive-path",
    envvar="ARCHIVE_PATH",
    help=(
        "Path to the archive storage directory. If defined, the archiver will "
        "save the `stream` in segments in the storage path."
    ),
    type=click.Path(),
)
@click.option(
    "--archive-segment-size",
    envvar="ARCHIVE_SEGMENT_SIZE",
    help="Archive segment size in seconds.",
    default=DEFAULT_ARCHIVE_SEGMENT_SIZE,
    show_default=True,
)
@click.option(
    "--archive-segment-filename",
    envvar="ARCHIVE_SEGMENT_FILENAME",
    help="Archive segment filename (without extension).",
    default=DEFAULT_ARCHIVE_SEGMENT_FILENAME,
    show_default=True,
)
@click.option(
    "--archive-segment-format",
    envvar="ARCHIVE_SEGMENT_FORMAT",
    help="Archive segment format.",
    default=DEFAULT_ARCHIVE_SEGMENT_FORMAT,
    show_default=True,
)
@click.option(
    "--archive-segment-format-options",
    envvar="ARCHIVE_SEGMENT_FORMAT_OPTIONS",
    help="Archive segment format options.",
)
@click.option(
    "--archive-copy-stream",
    envvar="ARCHIVE_COPY_STREAM",
    help=(
        "Copy the `stream` without transcoding (reduce CPU usage). "
        "WARNING: The stream has to be in the same format as the "
        "`--archive-segment-format`."
    ),
    is_flag=True,
)
def cli(
    listen_port: int,
    hook: Optional[str],
    stats_url: Optional[str],
    stats_user: str,
    stats_password: str,
    stream_url: Optional[str],
    silence_detect_noise: str,
    silence_detect_duration: str,
    archive_path: Optional[str],
    archive_segment_size: int,
    archive_segment_filename: str,
    archive_segment_format: str,
    archive_segment_format_options: Optional[str],
    archive_copy_stream: bool,
):
    """
    \b
    See the ffmpeg documentation for details about the `--archive-segment-*` options:
    https://ffmpeg.org/ffmpeg-formats.html#segment_002c-stream_005fsegment_002c-ssegment
    """

    if stream_url is None and stats_url is None:
        raise click.UsageError("Specify at least one of --stream-url or --stats-url.")

    # Setup stop mechanism
    stop_event = ThreadEvent()

    def stop_handler(_signum, _frame):
        logger.info("stopping...")
        stop_event.set()

    signal(SIGINT, stop_handler)
    signal(SIGTERM, stop_handler)

    # Setup event handler before doing any checks
    event_queue: Queue = Queue()
    event_handler = EventHandler(event_queue, stop_event)

    # Setup prometheus hook
    start_http_server(listen_port)
    event_handler.hooks.append(PrometheusHook())

    # Setup file hook
    if hook is not None:
        event_handler.hooks.append(FileHook(hook))

    event_handler.start()

    # Starting stats collector
    if stats_url is not None:
        stats_collector = StatsCollector(
            url=stats_url,
            auth=(stats_user, stats_password),
        )

    # Starting stream listener
    if stream_url is not None:
        while not stop_event.is_set():
            # Check the stream until it is available
            check_stream(event_queue, stop_event, stream_url)

            handlers: List[StreamListenerHandler] = [
                SilenceHandler(
                    event_queue=event_queue,
                    noise=silence_detect_noise,
                    duration=silence_detect_duration,
                )
            ]

            if archive_path is not None:
                handlers.append(
                    ArchiveHandler(
                        path=archive_path,
                        segment_size=archive_segment_size,
                        segment_filename=archive_segment_filename,
                        segment_format=archive_segment_format,
                        segment_format_options=archive_segment_format_options,
                        copy_stream=archive_copy_stream,
                    )
                )

            stream_listener = StreamListener(
                stream_url=stream_url,
                handlers=handlers,
            )
            stream_listener.run()

    event_handler.join()
    stats_collector.close()
