#!/usr/bin/env bash

set -e

error() {
  echo >&2 "$*"
  exit 1
}

[[ "$EVENT_KIND" == "start" ]] || error "invalid EVENT_KIND"
[[ "$EVENT_WHEN" == "2022-08-16T19:01:36.791399" ]] || error "invalid EVENT_WHEN"
[[ "$EVENT_SECONDS" == "0" ]] || error "invalid EVENT_SECONDS"
