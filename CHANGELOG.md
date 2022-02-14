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
