#!/usr/bin/env bash

set -u

error() {
  echo >&2 "error: $*"
  exit 1
}

archive_path="/mnt/archive"
archive_fileglob="archive-*.ogg"

[[ -d "$archive_path" ]] || error "$archive_path is not a directory!"

# Purge empty directories
find "$archive_path" -empty -type d -delete

printf -v today '%(%Y%m%d)T' -1

for path in $archive_path/$archive_fileglob; do
  filename=$(basename "$path")
  time=$(tmp="${filename#archive-}" && echo "${tmp:0:8}")

  if [[ "$time" == "$today" ]]; then
    echo "ignoring today's files $path"
    continue
  fi

  year="${time:0:4}"
  month="${time:4:2}"
  day="${time:6:2}"

  new_path="$archive_path/$year/$month/$day/$filename"

  echo "moving $path to $new_path"

  mkdir -p "$(dirname "$new_path")"
  mv "$path" "$new_path"
done
