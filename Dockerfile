FROM python:3.10-alpine as build

RUN pip install build

COPY . .
RUN python3 -m build

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
