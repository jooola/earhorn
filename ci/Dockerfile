ARG PYTHON_VERSION=3.10

FROM python:${PYTHON_VERSION}-slim as ci-python

RUN set -eux \
    && DEBIAN_FRONTEND=noninteractive apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    ffmpeg \
    git \
    make \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ARG PIP_NO_CACHE_DIR=1

RUN set -eux \
    && pip3 install --upgrade pip \
    && pip3 install setuptools wheel pipx \
    # https://python-poetry.org/docs/#installing-with-pipx
    && PIPX_BIN_DIR=/usr/local/bin pipx install poetry
