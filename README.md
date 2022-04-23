# earhorn

Listen, monitor and archive your streams!

[![](https://mermaid.ink/svg/pako:eNqNlD9PwzAQxb_KySNqFySWqCoDMLAw0AEhgiorvhIriV1dnAJCfHcuzj8nzsDmvHv383Muzo_IrEKRiNpJh_dafpCstpfr1AB4CVJxcJIc4AWNg1waVSKlAmTdGsgdB4k73q7eYbvdLwsx7Ey2QpdjU4ekQO06JkiADV0TWZ-O7aI-NlTCbpflVme436-DQnMCj35_V0PbqvCkDSq4jUN3ppU34AutfxZiSuy1BF4xTkwoq_9HHtx95vYxDj3ntr1ZjlnRi1GMVNy1ZSCsLD92ru50Yd9ablvEsUcEl06Wiq4QkhbHsYU_DQ90aGTsbZdwtlX3PoMzLOdT6tqhmY9m1CK3pCzXl7l71Lx7DLuGWhSnznCn58Z0eGqM0eZjGu0A84ioOtCW1X7pZb5rCTx8abe4X2gUIJElcHb10rLh6A1L4lRh8GCIRxC4nux88xepHfDU4YZtmTWqv96frE8Y3zFSPDQ2zJXoMxYbUSFVUiv-d_20DangT6jCVCS85Ashm9KlIjW_bG3OigM-KO0sieQkyxo3QjbOHr5NJhJHDQ6m_hfYu37_AFEs0XE)](https://mermaid.live/edit#pako:eNqNlD9PwzAQxb_KySNqFySWqCoDMLAw0AEhgiorvhIriV1dnAJCfHcuzj8nzsDmvHv383Muzo_IrEKRiNpJh_dafpCstpfr1AB4CVJxcJIc4AWNg1waVSKlAmTdGsgdB4k73q7eYbvdLwsx7Ey2QpdjU4ekQO06JkiADV0TWZ-O7aI-NlTCbpflVme436-DQnMCj35_V0PbqvCkDSq4jUN3ppU34AutfxZiSuy1BF4xTkwoq_9HHtx95vYxDj3ntr1ZjlnRi1GMVNy1ZSCsLD92ru50Yd9ablvEsUcEl06Wiq4QkhbHsYU_DQ90aGTsbZdwtlX3PoMzLOdT6tqhmY9m1CK3pCzXl7l71Lx7DLuGWhSnznCn58Z0eGqM0eZjGu0A84ioOtCW1X7pZb5rCTx8abe4X2gUIJElcHb10rLh6A1L4lRh8GCIRxC4nux88xepHfDU4YZtmTWqv96frE8Y3zFSPDQ2zJXoMxYbUSFVUiv-d_20DangT6jCVCS85Ashm9KlIjW_bG3OigM-KO0sieQkyxo3QjbOHr5NJhJHDQ6m_hfYu37_AFEs0XE)

## Install

If you need to listen or archive an Icecast stream, you will need `ffmpeg`:

```sh
sudo apt install ffmpeg
```

Install earhorn from pip:

```sh
pip install earhorn
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

  See the ffmpeg documentation for details about the `--archive-segment-*` options:
  https://ffmpeg.org/ffmpeg-formats.html#segment_002c-stream_005fsegment_002c-ssegment

Options:
  --listen-port INTEGER           Listen port for the prometheus metrics endpoint.  [default: 9950]
  --hook PATH                     Path to a custom script executed to handle stream state `events`.
  --stream-url TEXT               URL to the icecast stream.
  --stats-url TEXT                URL to the icecast admin xml stats page.
  --stats-user TEXT               Username for the icecast admin xml stats page.  [default: admin]
  --stats-password TEXT           Password for the icecast admin xml stats page.
  --archive-path PATH             Path to the archive storage directory. If defined, the archiver will save the
                                  `stream` in segments in the storage path.
  --archive-segment-size INTEGER  Archive segment size in seconds.  [default: 3600]
  --archive-segment-filename TEXT
                                  Archive segment filename (without extension).  [default: archive-%Y%m%d_%H%M%S]
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
