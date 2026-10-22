FROM python:3.15-alpine@sha256:d44b1254cb92329418d164b22b20d86bbd3869d48e80e09e476531a409a728bb AS build

RUN set -eux; \
    pip --no-cache-dir install --no-compile build

WORKDIR /src
COPY . .
RUN set -eux; \
    python3 -m build

FROM python:3.15-alpine@sha256:d44b1254cb92329418d164b22b20d86bbd3869d48e80e09e476531a409a728bb AS base

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
