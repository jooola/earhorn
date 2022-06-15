# earhorn

Listen, monitor and archive your streams!

[![](https://mermaid.ink/svg/pako:eNqNlD9PwzAQxb_KySNqFySWqCoDMLAw0AEhgiorvhIriV1dnAJCfHcuzj8nzsDmvHv383Muzo_IrEKRiNpJh_dafpCstpfr1AB4CVJxcJIc4AWNg1waVSKlAmTdGsgdB4k73q7eYbvdLwsx7Ey2QpdjU4ekQO06JkiADV0TWZ-O7aI-NlTCbpflVme436-DQnMCj35_V0PbqvCkDSq4jUN3ppU34AutfxZiSuy1BF4xTkwoq_9HHtx95vYxDj3ntr1ZjlnRi1GMVNy1ZSCsLD92ru50Yd9ablvEsUcEl06Wiq4QkhbHsYU_DQ90aGTsbZdwtlX3PoMzLOdT6tqhmY9m1CK3pCzXl7l71Lx7DLuGWhSnznCn58Z0eGqM0eZjGu0A84ioOtCW1X7pZb5rCTx8abe4X2gUIJElcHb10rLh6A1L4lRh8GCIRxC4nux88xepHfDU4YZtmTWqv96frE8Y3zFSPDQ2zJXoMxYbUSFVUiv-d_20DangT6jCVCS85Ashm9KlIjW_bG3OigM-KO0sieQkyxo3QjbOHr5NJhJHDQ6m_hfYu37_AFEs0XE)](https://mermaid.live/edit#pako:eNqNlD9PwzAQxb_KySNqFySWqCoDMLAw0AEhgiorvhIriV1dnAJCfHcuzj8nzsDmvHv383Muzo_IrEKRiNpJh_dafpCstpfr1AB4CVJxcJIc4AWNg1waVSKlAmTdGsgdB4k73q7eYbvdLwsx7Ey2QpdjU4ekQO06JkiADV0TWZ-O7aI-NlTCbpflVme436-DQnMCj35_V0PbqvCkDSq4jUN3ppU34AutfxZiSuy1BF4xTkwoq_9HHtx95vYxDj3ntr1ZjlnRi1GMVNy1ZSCsLD92ru50Yd9ablvEsUcEl06Wiq4QkhbHsYU_DQ90aGTsbZdwtlX3PoMzLOdT6tqhmY9m1CK3pCzXl7l71Lx7DLuGWhSnznCn58Z0eGqM0eZjGu0A84ioOtCW1X7pZb5rCTx8abe4X2gUIJElcHb10rLh6A1L4lRh8GCIRxC4nux88xepHfDU4YZtmTWqv96frE8Y3zFSPDQ2zJXoMxYbUSFVUiv-d_20DangT6jCVCS85Ashm9KlIjW_bG3OigM-KO0sieQkyxo3QjbOHr5NJhJHDQ6m_hfYu37_AFEs0XE)

## Install

If you need to listen or archive an Icecast stream, you will need `ffmpeg`:

```sh
sudo apt install ffmpeg
```

Install earhorn from pip (install the s3 extra to upload the segment to an s3 bucket):

```sh
pip install earhorn
pip install earhorn[s3]
```

You can start archiving an Icecast stream by providing a stream url and an archive path:

```sh
earhorn \
  --stream-url https://stream.example.org/live.ogg \
  --archive-path=/to/my/archive
```

You can also start exporting the Icecast stats as prometheus metrics by providing an Icecast stats url:

```sh
earhorn \
  --stats-url https://stream.example.org/admin/stats.xml \
  --stats-user admin \
  --stats-password hackme
```

### Docker

```sh
docker pull ghcr.io/jooola/earhorn
```

## Usage

```
Usage: earhorn [OPTIONS]

  ENVIRONMENT VARIABLES:

  If a `.env` file is present in the current directory, it will be loaded and can be used to pass environment
  variables to this tool.

  ARCHIVE STORAGE:

  The storage can be defined using a path to a local directory or an url to an s3 bucket. Segments will be saved on
  the storage you specified.

  To use an s3 bucket, you need to install the `s3` extras (`pip install earhorn[s3]`), use `s3://bucket-name` as
  value for the `--archive-path` option and export the s3 bucket credentials listed in the table below:

  | Variable                | Description                               | Example                     |
  | ----------------------- | ----------------------------------------- | --------------------------- |
  | AWS_ACCESS_KEY_ID       | The access key for your bucket user       | AKIA568knmklmk              |
  | AWS_SECRET_ACCESS_KEY   | The secret key for your bucket user       | mi0y84wu498zxsasa           |
  | AWS_S3_ENDPOINT_URL     | The endpoint to your s3 bucket (optional) | https://s3.nl-ams.scw.cloud |
  | AWS_S3_REGION_NAME      | Region of your s3 bucket                  | us-east-2                   |

  Example: export AWS_S3_ENPOINT_URL="https://s3.nl-ams.scw.cloud"

  ARCHIVE SEGMENTS:

  To change the segments duration or format, see the ffmpeg documentation for details
  about the available options:
  https://ffmpeg.org/ffmpeg-formats.html#segment_002c-stream_005fsegment_002c-ssegment

Options:
  --listen-port INTEGER           Listen port for the prometheus metrics endpoint.  [default: 9950]
  --hook PATH                     Path to a custom script executed to handle stream state `events`.
  --stats-url TEXT                URL to the icecast admin xml stats page.
  --stats-user TEXT               Username for the icecast admin xml stats page.  [default: admin]
  --stats-password TEXT           Password for the icecast admin xml stats page.
  --stream-url TEXT               URL to the icecast stream.
  --silence-detect-noise TEXT     Silence detect noise.  [default: -60dB]
  --silence-detect-duration TEXT  Silence detect duration.  [default: 2]
  --archive-path PATH             Path or url to the archive storage, supported storage are local filesystem and s3.
                                  If defined, the stream will be archived in the storage as segments.
  --archive-segment-filepath TEXT
                                  Archive segment filepath.  [default:
                                  {year}/{month}/{day}/{hour}{minute}{second}.{format}]
  --archive-segment-size INTEGER  Archive segment size in seconds.  [default: 3600]
  --archive-segment-format TEXT   Archive segment format.  [default: ogg]
  --archive-segment-format-options TEXT
                                  Archive segment format options.
  --archive-copy-stream           Copy the `stream` without transcoding (reduce CPU usage). WARNING: The stream has to
                                  be in the same format as the `--archive-segment-format`.
  --help                          Show this message and exit.

```

## Developmement

To develop this project, start by reading the `Makefile` to have a basic understanding of the possible tasks.

Install the project and the dependencies in a virtual environment:

```sh
make install
source .venv/bin/activate
earhorn --help
```

## Releases

To release a new version, first bump the version number in `pyproject.toml` by hand or by using:

```sh
# poetry version --help
poetry version <patch|minor|major>
```

Run the release target:

```sh
make release
```

Finally, push the release commit and tag to publish them to Pypi:

```sh
git push --follow-tags
```
