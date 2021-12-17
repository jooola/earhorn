FROM python:3.10-alpine

RUN apk add --no-cache ffmpeg

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install earhorn

ENTRYPOINT ["earhorn"]
