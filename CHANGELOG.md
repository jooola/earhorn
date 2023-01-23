<a name="v0.15.0-alpha.1"></a>

## [v0.15.0-alpha.1](https://github.com/jooola/earhorn/compare/v0.15.0-alpha.0...v0.15.0-alpha.1) (2023-01-23)

### :bug: Bug Fixes

- use logger name instead of module

### :rocket: Features

- improve log level handling

<a name="v0.15.0-alpha.0"></a>

## [v0.15.0-alpha.0](https://github.com/jooola/earhorn/compare/v0.14.0...v0.15.0-alpha.0) (2023-01-23)

### :rocket: Features

- replace loguru with logging
- add sentry python integration

<a name="v0.14.0"></a>

## [v0.14.0](https://github.com/jooola/earhorn/compare/v0.14.0a0...v0.14.0) (2023-01-23)

### :bug: Bug Fixes

- handle encoding errors in ffmpeg stderr
- queue 'type' object is not subscriptable

<a name="v0.14.0a0"></a>

## [v0.14.0a0](https://github.com/jooola/earhorn/compare/v0.13.1...v0.14.0a0) (2023-01-10)

### :bug: Bug Fixes

- do not hang on container shutdown
- catch and ignore invalid segment filename

### :rocket: Features

- rework container image
- remove inaccurate validate_silence_duration

<a name="v0.13.1"></a>

## [v0.13.1](https://github.com/jooola/earhorn/compare/v0.13.0...v0.13.1) (2022-11-04)

### :bug: Bug Fixes

- catch timeout / network errors for stream check

### :gear: CI/CD

- use python 3.10 as stable version
- split install and test step
- build lxml for python 3.11
- test python3.11

<a name="v0.13.0"></a>

## [v0.13.0](https://github.com/jooola/earhorn/compare/v0.13.0-alpha.0...v0.13.0) (2022-10-07)

<a name="v0.13.0-alpha.0"></a>

## [v0.13.0-alpha.0](https://github.com/jooola/earhorn/compare/v0.12.0...v0.13.0-alpha.0) (2022-10-07)

### :bug: Bug Fixes

- catch client errors and failed s3 uploads
- clean old fifo before creating it
- use default max_attempts for s3 retry strategy

### :gear: CI/CD

- allow testing docker build
- publish container to docker.io

### :rocket: Features

- use pending dir for failed segment ingestion
- set working dir to /app in container
- save segments in the working dir before archiving

### BREAKING CHANGE

We now save temporary segments in `$PWD/<some_dir>` directory, this means that earhorn has to run in a dedicated directory such as `/var/lib/earhorn`.

<a name="v0.12.0"></a>

## [v0.12.0](https://github.com/jooola/earhorn/compare/v0.11.5...v0.12.0) (2022-10-07)

### :bug: Bug Fixes

- catch boto connection errors

### :rocket: Features

- add boto default retry strategy

<a name="v0.11.5"></a>

## [v0.11.5](https://github.com/jooola/earhorn/compare/v0.11.4...v0.11.5) (2022-10-04)

### :bug: Bug Fixes

- improve logging in stream_silence
- set default silence duration to decimal value

<a name="v0.11.4"></a>

## [v0.11.4](https://github.com/jooola/earhorn/compare/v0.11.3...v0.11.4) (2022-09-20)

### :bug: Bug Fixes

- recreate segments.csv fifo when restarting the listener

<a name="v0.11.3"></a>

## [v0.11.3](https://github.com/jooola/earhorn/compare/v0.11.2...v0.11.3) (2022-08-16)

### :bug: Bug Fixes

- replace events float with decimal
- allow 0.1 difference between durations

<a name="v0.11.2"></a>

## [v0.11.2](https://github.com/jooola/earhorn/compare/v0.11.1...v0.11.2) (2022-08-09)

### :bug: Bug Fixes

- let the parser guess the content encoding

<a name="v0.11.1"></a>

## [v0.11.1](https://github.com/jooola/earhorn/compare/v0.11.0...v0.11.1) (2022-08-09)

### :bug: Bug Fixes

- disable resolve_entities on xml parser

### :gear: CI/CD

- run linting and testing in parallel

<a name="v0.11.0"></a>

## [v0.11.0](https://github.com/jooola/earhorn/compare/v0.11.0-alpha.3...v0.11.0) (2022-06-20)

<a name="v0.11.0-alpha.3"></a>

## [v0.11.0-alpha.3](https://github.com/jooola/earhorn/compare/v0.11.0-alpha.2...v0.11.0-alpha.3) (2022-06-15)

<a name="v0.11.0-alpha.2"></a>

## [v0.11.0-alpha.2](https://github.com/jooola/earhorn/compare/v0.11.0-alpha.1...v0.11.0-alpha.2) (2022-06-15)

### :bug: Bug Fixes

- join command args in debug log
- dot not log event using json
- only close stats collector when used
- always close httpx client

### :rocket: Features

- add s3 segment storage
- load .env on run
- wait and handle segments using a fifo
- move check_stream in stream listener

### BREAKING CHANGE

The `--archive-segment-filename` option has been
replace with `--archive-segment-filepath`, and uses an new template syntax.

<a name="v0.11.0-alpha.1"></a>

## [v0.11.0-alpha.1](https://github.com/jooola/earhorn/compare/v0.11.0-alpha.0...v0.11.0-alpha.1) (2022-05-03)

### :bug: Bug Fixes

- reorder cli flags
- update log message
- improve logging in stats collector

### :rocket: Features

- allow tweaking silence detect settings
- listen stream with a single ffmpeg command ([#73](https://github.com/jooola/earhorn/issues/73))

<a name="v0.11.0-alpha.0"></a>

## [v0.11.0-alpha.0](https://github.com/jooola/earhorn/compare/v0.10.1...v0.11.0-alpha.0) (2022-05-03)

### :bug: Bug Fixes

- improve perf sharing a httpx client instance
- catch errors from flaky icecasts servers

### :rocket: Features

- reduce event handler queue timeout to 2s

<a name="v0.10.1"></a>

## [v0.10.1](https://github.com/jooola/earhorn/compare/v0.10.0...v0.10.1) (2022-04-27)

### :bug: Bug Fixes

- don't import internal Collector class

<a name="v0.10.0"></a>

## [v0.10.0](https://github.com/jooola/earhorn/compare/v0.9.0...v0.10.0) (2022-04-27)

### :rocket: Features

- icecast stats using a prometheus custom collector

<a name="v0.9.0"></a>

## [v0.9.0](https://github.com/jooola/earhorn/compare/v0.9.0-alpha.3...v0.9.0) (2022-04-25)

<a name="v0.9.0-alpha.3"></a>

## [v0.9.0-alpha.3](https://github.com/jooola/earhorn/compare/v0.9.0-alpha.2...v0.9.0-alpha.3) (2022-04-24)

### :bug: Bug Fixes

- prevent looping during silence_listener/archiver start

<a name="v0.9.0-alpha.2"></a>

## [v0.9.0-alpha.2](https://github.com/jooola/earhorn/compare/v0.9.0-alpha.1...v0.9.0-alpha.2) (2022-04-24)

### :bug: Bug Fixes

- add stats exporter to thread list
- infinity loop when stream_url is not provided
- do not stop stats thread on read Timeout

### :rocket: Features

- start even_handler earlier
- rebuild prometheus icecast exporter
- raise error if no stream or stats url is provided

<a name="v0.9.0-alpha.1"></a>

## [v0.9.0-alpha.1](https://github.com/jooola/earhorn/compare/v0.9.0-alpha.0...v0.9.0-alpha.1) (2022-04-24)

### :rocket: Features

- add stats extraction time metric

<a name="v0.9.0-alpha.0"></a>

## [v0.9.0-alpha.0](https://github.com/jooola/earhorn/compare/v0.8.2...v0.9.0-alpha.0) (2022-04-24)

### :rocket: Features

- add icecast stats parser
- become a prometheus exporter
- replace url argument with --stream-url flag
- rename handler to event_handler
- update zabbix integrations template

<a name="v0.8.2"></a>

## [v0.8.2](https://github.com/jooola/earhorn/compare/v0.8.1...v0.8.2) (2022-02-19)

### :bug: Bug Fixes

- assume no silence when silence listener start

<a name="v0.8.1"></a>

## [v0.8.1](https://github.com/jooola/earhorn/compare/v0.8.0...v0.8.1) (2022-02-19)

### :bug: Bug Fixes

- prevent hook to stop the event handler on error
- executable bit on organizer script
- only trigger zabbix alert ~15s of silence

### :rocket: Features

- add template for zabbix monitoring

<a name="v0.8.0"></a>

## [v0.8.0](https://github.com/jooola/earhorn/compare/v0.8.0-alpha.0...v0.8.0) (2022-02-14)

### :rocket: Features

- allow to override ffmpeg executable path

### Reverts

- feat: remove -re flag

<a name="v0.8.0-alpha.0"></a>

## [v0.8.0-alpha.0](https://github.com/jooola/earhorn/compare/v0.7.0...v0.8.0-alpha.0) (2022-02-09)

### :rocket: Features

- remove -re flag

<a name="v0.7.0"></a>

## [v0.7.0](https://github.com/jooola/earhorn/compare/v0.6.0...v0.7.0) (2022-02-05)

### :rocket: Features

- rename prometheus metrics names

<a name="v0.6.0"></a>

## [v0.6.0](https://github.com/jooola/earhorn/compare/v0.5.2...v0.6.0) (2022-02-05)

### :bug: Bug Fixes

- py37 compatibility fix for Protocol
- py37 compatibility fix for Literal
- type object not being subscriptable

### :gear: CI/CD

- add py310 to the test matrix

### :rocket: Features

- enhance cli usage
- allow to transcode the stream for archiving ([#37](https://github.com/jooola/earhorn/issues/37))
- add prometheus metrics endpoint ([#36](https://github.com/jooola/earhorn/issues/36))

<a name="v0.5.2"></a>

## v0.5.2 (2022-02-03)

### :bug: Bug Fixes

- remove extension from archive segment filename
- always flush event queue on stop ([#24](https://github.com/jooola/earhorn/issues/24))
- linting
- don't use stderr.readline
- log formatting
- update apt packages list in ci
- no tests yet
- tests module not yet created

### :gear: CI/CD

- docker-publish does not need publish job

### :rocket: Features

- use event handler and checks during startup
- add stream url precheck ([#20](https://github.com/jooola/earhorn/issues/20))
- more logging for silence listener
- more logging for archiver
- create docker image and publish it ([#19](https://github.com/jooola/earhorn/issues/19))
- use realtime input ([#10](https://github.com/jooola/earhorn/issues/10))
- silence detect ([#9](https://github.com/jooola/earhorn/issues/9))
- warn when no action will be taken
- allow url to be specified using env var
- initial work
