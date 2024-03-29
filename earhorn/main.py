import logging
import os
from queue import Queue
from signal import SIGINT, SIGTERM, signal
from threading import Event as ThreadEvent
from typing import Callable, Optional

import click
from dotenv import load_dotenv
from prometheus_client import start_http_server

from . import version
from .event import EventHandler, FileHook, PrometheusHook
from .stats import StatsCollector
from .stream import StreamListener, StreamListenerHandler
from .stream_archive import (
    DEFAULT_ARCHIVE_SEGMENT_FILEPATH,
    DEFAULT_ARCHIVE_SEGMENT_FORMAT,
    DEFAULT_ARCHIVE_SEGMENT_SIZE,
    ArchiveHandler,
    ArchiveStorage,
    LocalArchiveStorage,
)
from .stream_silence import (
    DEFAULT_SILENCE_DETECT_DURATION,
    DEFAULT_SILENCE_DETECT_NOISE,
    DEFAULT_SILENCE_DETECT_RAW,
    SilenceHandler,
)

for module in ("httpx", "urllib3", "botocore", "s3transfer"):
    logging.getLogger(module).setLevel(logging.INFO)
    logging.getLogger(module).propagate = False

logger = logging.getLogger(__name__)


load_dotenv()


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
    "--hook-log-stderr",
    envvar="HOOK_LOG_STDERR",
    help="Log the hook stderr output.",
    is_flag=True,
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
    "--silence-detect-raw",
    envvar="SILENCE_DETECT_RAW",
    help=(
        "Silence detect ffmpeg raw filter. Can be used "
        "to add extra filters (e.g. highpass) or extra "
        "options to the silencedetect filter."
    ),
    default=DEFAULT_SILENCE_DETECT_RAW,
    show_default=True,
)
@click.option(
    "--archive-path",
    envvar="ARCHIVE_PATH",
    help=(
        "Path or url to the archive storage, supported "
        "storage are local filesystem and s3. If defined, "
        "the stream will be archived in the storage as "
        "segments."
    ),
    type=click.Path(),
)
@click.option(
    "--archive-segment-filepath",
    envvar="ARCHIVE_SEGMENT_FILEPATH",
    help="Archive segment filepath.",
    default=DEFAULT_ARCHIVE_SEGMENT_FILEPATH,
    show_default=True,
)
@click.option(
    "--archive-segment-size",
    envvar="ARCHIVE_SEGMENT_SIZE",
    help="Archive segment size in seconds.",
    default=DEFAULT_ARCHIVE_SEGMENT_SIZE,
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
@click.option(
    "--log-level",
    envvar="LOG_LEVEL",
    help="Logging level.",
    default="info",
    show_default=True,
    type=click.Choice(
        ["critical", "error", "warning", "info", "debug"],
        case_sensitive=False,
    ),
)
def cli(
    listen_port: int,
    hook: Optional[str],
    hook_log_stderr: bool,
    stats_url: Optional[str],
    stats_user: str,
    stats_password: str,
    stream_url: Optional[str],
    silence_detect_noise: str,
    silence_detect_duration: str,
    silence_detect_raw: str,
    archive_path: Optional[str],
    archive_segment_filepath: str,
    archive_segment_size: int,
    archive_segment_format: str,
    archive_segment_format_options: Optional[str],
    archive_copy_stream: bool,
    log_level: str,
):
    # pylint: disable=line-too-long
    """
    ENVIRONMENT VARIABLES:

    If a `.env` file is present in the current directory, it will be loaded
    and can be used to pass environment variables to this tool.

    ARCHIVE STORAGE:

    The storage can be defined using a path to a local directory or an
    url to an s3 bucket. Segments will be saved on the storage you
    specified.

    To use an s3 bucket, you need to install the `s3` extras (`pip install earhorn[s3]`),
    use `s3://bucket-name` as value for the `--archive-path` option and export the
    s3 bucket credentials listed in the table below:

    \b
    | Variable                | Description                               | Example                     |
    | ----------------------- | ----------------------------------------- | --------------------------- |
    | AWS_ACCESS_KEY_ID       | The access key for your bucket user       | AKIA568knmklmk              |
    | AWS_SECRET_ACCESS_KEY   | The secret key for your bucket user       | mi0y84wu498zxsasa           |
    | AWS_S3_ENDPOINT_URL     | The endpoint to your s3 bucket (optional) | https://s3.nl-ams.scw.cloud |
    | AWS_S3_REGION_NAME      | Region of your s3 bucket                  | us-east-2                   |

    Example: export AWS_S3_ENPOINT_URL="https://s3.nl-ams.scw.cloud"

    ARCHIVE SEGMENTS:

    \b
    To change the segments duration or format, see the ffmpeg documentation for details
    about the available options:
    https://ffmpeg.org/ffmpeg-formats.html#segment_002c-stream_005fsegment_002c-ssegment

    HOOK SCRIPT:

    To handle events using a custom script, define the `--hook` option with a path to
    your script. This script will not receive any arguments, and the event details will be
    passed via environment variables.

    \b
    | Event   | Environment variables | Values                                                |
    | ------- | --------------------- | ----------------------------------------------------- |
    | status  |                       |                                                       |
    |         | EVENT_NAME            | `status`                                              |
    |         | EVENT_KIND            | `up` or `down`                                        |
    |         | EVENT_WHEN            | ISO 8601 datetime                                     |
    | silence |                       |                                                       |
    |         | EVENT_NAME            | `silence`                                             |
    |         | EVENT_KIND            | `start` or `end`                                      |
    |         | EVENT_WHEN            | ISO 8601 datetime                                     |
    |         | EVENT_DURATION        | Duration in seconds (only available on silence end) |
    """
    logging.basicConfig(
        level=log_level.upper(),
        format="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)s - %(message)s",
    )

    if "SENTRY_DSN" in os.environ:
        logger.info("installing sentry")
        # pylint: disable=import-outside-toplevel
        import sentry_sdk

        sentry_sdk.init(
            traces_sample_rate=1.0,
            release=version,
        )

    if stream_url is None and stats_url is None:
        raise click.UsageError("Specify at least one of --stream-url or --stats-url.")

    # Setup stop mechanism
    stop_event = ThreadEvent()
    stop_functions: list[Callable] = []

    def stop_handler(_signum, _frame):
        logger.info("stopping...")
        stop_event.set()

        for function in stop_functions:
            function()

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
        event_handler.hooks.append(FileHook(hook, hook_log_stderr))

    event_handler.start()

    # Starting stats collector
    if stats_url is not None:
        stats_collector = StatsCollector(
            url=stats_url,
            auth=(stats_user, stats_password),
        )

    # Starting stream listener
    if stream_url is not None:
        handlers: list[StreamListenerHandler] = [
            SilenceHandler(
                stop=stop_event,
                event_queue=event_queue,
                noise=silence_detect_noise,
                duration=silence_detect_duration,
                raw=silence_detect_raw,
            )
        ]

        if archive_path is not None:
            archive_storage: ArchiveStorage

            if archive_path.startswith("s3://"):
                # pylint: disable=import-outside-toplevel
                from .stream_archive_s3 import S3ArchiveStorage

                archive_storage = S3ArchiveStorage(archive_path)
            else:
                archive_storage = LocalArchiveStorage(archive_path)

            handlers.append(
                ArchiveHandler(
                    stop=stop_event,
                    storage=archive_storage,
                    segment_size=archive_segment_size,
                    segment_filepath=archive_segment_filepath,
                    segment_format=archive_segment_format,
                    segment_format_options=archive_segment_format_options,
                    copy_stream=archive_copy_stream,
                )
            )

        stream_listener = StreamListener(
            stop=stop_event,
            event_queue=event_queue,
            stream_url=stream_url,
            handlers=handlers,
        )
        stop_functions.append(stream_listener.stop_listener)
        stream_listener.run_forever()

    event_handler.join()

    if stats_url is not None:
        stats_collector.close()


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    cli()
