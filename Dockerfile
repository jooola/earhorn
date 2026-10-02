FROM python:3.14-alpine@sha256:2e740b2c28a426e74f11396c05e38afb3191acced75045b8d62df573c1dc8ce8 AS build

RUN set -eux; \
    pip --no-cache-dir install --no-compile build

WORKDIR /src
COPY . .
RUN set -eux; \
    python3 -m build

FROM python:3.14-alpine@sha256:2e740b2c28a426e74f11396c05e38afb3191acced75045b8d62df573c1dc8ce8 AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Custom user
ARG USER=earhorn
ARG UID=1000
ARG GID=1000

RUN set -eux; \
    adduser --disabled-password --uid=$UID --gecos '' --no-create-home ${USER}; \
    install --directory --owner=${USER} /app

# Install ffmpeg
RUN set -eux; \
    apk add --no-cache ffmpeg

# Development target
FROM base AS dev

# Install earhorn
WORKDIR /src
COPY . .
RUN set -eux; \
    pip --no-cache-dir install --editable .[s3]

# Run
USER ${UID}:${GID}
WORKDIR /app
ENTRYPOINT ["/usr/local/bin/earhorn"]

# Production target
FROM base

# Install earhorn
WORKDIR /src
COPY --from=build /src/dist/*.whl .
RUN set -eux; \
    export WHEEL=$(echo *.whl); \
    pip --no-cache-dir install --no-compile "${WHEEL}[s3]"; \
    rm -Rf /src

# Run
USER ${UID}:${GID}
WORKDIR /app
ENTRYPOINT ["/usr/local/bin/earhorn"]
