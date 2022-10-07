FROM python:3.10-bullseye as build

RUN pip install poetry

COPY . .
RUN poetry build

FROM python:3.10-alpine

RUN apk add --no-cache ffmpeg

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY --from=build dist/*.whl .
RUN export WHEEL=$(echo *.whl) && \
    pip install "${WHEEL}[s3]" && \
    rm -Rf *.whl

WORKDIR /app
ENTRYPOINT ["earhorn"]
