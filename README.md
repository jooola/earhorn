# earhorn

Listen, monitor and archive your streams!

[![](https://mermaid.ink/svg/pako:eNqFkzFPwzAQhf_KySNqFySWqCoDdGBhoANCBEWWfW2sNja6XAqo6n_HdeIkboPIFL_77p3zYh-FchpFJmqWjI9GbklW88NtbsE_QYRcrFkSAx7QMpTS6j1SLkDWZ4C4iFLoeb_5gPl8eVlKDR9KVDsgrJxf1kwoq9ZQnQtFp8SWwSc4p8zY2Gw6uXA7WCxU6YzC5XKMBDtf2zjaxcrYMEwY-2TwVAOXcZvgne_j1GRe_9EZvGE9FeDe1Iw2za7XJnhC5UinfK8N4YzivnJLqkPvxTS0GpDIEbCb_M0eKAKQNr5Kw-CThDuPKGd13fJfXh-S-Sur3jSDZ9cZ91pApnxS7Z8DkYuXxrZ7osZaY7fjQxXTCiYT9ZhXWm-Jbnk1P4NVm9M15m-Gr34bFjNRIVXSaH_xjmcwF_6EVZiLzL9q3Mhmz7nI7cmjzaf2n7LShh2JjKnBmZANu_WPVXHdMt31bcXTL1HtUgA)](https://mermaid.live/edit/#pako:eNqFkzFPwzAQhf_KySNqFySWqCoDdGBhoANCBEWWfW2sNja6XAqo6n_HdeIkboPIFL_77p3zYh-FchpFJmqWjI9GbklW88NtbsE_QYRcrFkSAx7QMpTS6j1SLkDWZ4C4iFLoeb_5gPl8eVlKDR9KVDsgrJxf1kwoq9ZQnQtFp8SWwSc4p8zY2Gw6uXA7WCxU6YzC5XKMBDtf2zjaxcrYMEwY-2TwVAOXcZvgne_j1GRe_9EZvGE9FeDe1Iw2za7XJnhC5UinfK8N4YzivnJLqkPvxTS0GpDIEbCb_M0eKAKQNr5Kw-CThDuPKGd13fJfXh-S-Sur3jSDZ9cZ91pApnxS7Z8DkYuXxrZ7osZaY7fjQxXTCiYT9ZhXWm-Jbnk1P4NVm9M15m-Gr34bFjNRIVXSaH_xjmcwF_6EVZiLzL9q3Mhmz7nI7cmjzaf2n7LShh2JjKnBmZANu_WPVXHdMt31bcXTL1HtUgA)

## Install

```sh
sudo apt install ffmpeg
pip install earhorn
```

```sh
earhorn --archive-path=/to/my/archive https://stream.example.org/live.ogg
```

### Docker

```sh
docker pull ghcr.io/jooola/earhorn
```

## Usage

```
Usage: earhorn [OPTIONS] URL

  URL of the `stream`.

  See the ffmpeg documentation for details about the `--archive-segment-*` options:
  https://ffmpeg.org/ffmpeg-formats.html#segment_002c-stream_005fsegment_002c-ssegment

Options:
  --hook PATH                     Path to a custom script executed to handle stream state `events`.
  --prometheus                    Enable the prometheus metrics endpoint. The endpoint expose the state of the
                                  `stream`
  --prometheus-listen-port INTEGER
                                  Listen port for the prometheus metrics endpoint.  [default: 9950]
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
