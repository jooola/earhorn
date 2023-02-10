ARG PYTHON_VERSION=3.10

FROM python:${PYTHON_VERSION}-slim as ci-python

RUN set -eux \
    && DEBIAN_FRONTEND=noninteractive apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    curl \
    git \
    gpg \
    make \
    && rm -rf /var/lib/apt/lists/*

RUN set -eux \
    && mkdir -m 0755 -p /etc/apt/keyrings \
    && curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg \
    && echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian bullseye stable" \
    | tee /etc/apt/sources.list.d/docker.list \
    && DEBIAN_FRONTEND=noninteractive apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    docker \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/* \
    && install -m 755 <(echo -e '#!/usr/bin/env bash\nexec docker compose "$@"') /usr/local/bin/docker-compose

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ARG PIP_NO_CACHE_DIR=1

RUN set -eux \
    && pip3 install --upgrade pip \
    && pip3 install setuptools wheel pipx \
    # https://python-poetry.org/docs/#installing-with-pipx
    && PIPX_BIN_DIR=/usr/local/bin pipx install poetry
