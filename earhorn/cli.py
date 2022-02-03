import click

from .archive import TIMESTAMP_FORMAT
from .earhorn import run


@click.command(context_settings={"max_content_width": 120})
@click.option(
    "--hook",
    envvar="HOOK",
    help="Hook to run to handle events.",
    type=click.Path(),
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
def main(**kwargs):
    """
    URL of the stream.
    """
    run(**kwargs)
