FROM python:3.11-alpine as build

RUN set -eux; \
    pip --no-cache-dir install --no-compile build

WORKDIR /src
COPY . .
RUN set -eux; \
    python3 -m build

FROM python:3.11-alpine as base

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
FROM base as dev

# Install earhorn
WORKDIR /src
COPY . .
RUN set -eux; \
    pip --no-cache-dir install --editable .[s3,sentry]

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
    pip --no-cache-dir install --no-compile "${WHEEL}[s3,sentry]"; \
    rm -Rf /src

# Run
USER ${UID}:${GID}
WORKDIR /app
ENTRYPOINT ["/usr/local/bin/earhorn"]
