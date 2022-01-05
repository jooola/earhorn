import click

from .archive import TIMESTAMP_FORMAT
from .earhorn import listen


@click.command()
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
)
@click.option(
    "--archive-segment-filename",
    envvar="ARCHIVE_SEGMENT_FILENAME",
    help="Archive segment filename.",
    default=f"archive-{TIMESTAMP_FORMAT}.ogg",
)
@click.option(
    "--archive-segment-format",
    envvar="ARCHIVE_SEGMENT_FORMAT",
    help="Archive segment format.",
    default="ogg",
)
@click.argument("url")
def run(**kwargs):
    """
    URL of the stream.
    """
    listen(**kwargs)
