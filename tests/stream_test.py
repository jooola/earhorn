from datetime import datetime
from decimal import Decimal
from pathlib import Path
from queue import Queue
from threading import Event as ThreadEvent
from unittest.mock import Mock, patch

import pytest

from earhorn.stream import StreamListener
from earhorn.stream_silence import SilenceEvent, SilenceHandler, parse_silence_detect

now = datetime.now()
here = Path(__file__).parent


SILENCE_DETECT_RAW = """
[silencedetect @ 0x559578eea680] silence_start: 52.697
[silencedetect @ 0x559578eea680] silence_end: 55.23 | silence_duration: 2.53304
[silencedetect @ 0x55ef37b94c80] silence_start: 2216
[silencedetect @ 0x55ef37b94c80] silence_end: 2218.73 | silence_duration: 2.73506
[silencedetect @ 0x55ef37b94c80] silence_start: 2421.39
[silencedetect @ 0x55ef37b94c80] silence_end: 2423.92 | silence_duration: 2.53304
"""

SILENCE_DETECT_EVENTS = [
    SilenceEvent(when=now, kind="start", seconds=Decimal("52.697"), duration=None),
    SilenceEvent(
        when=now,
        kind="end",
        seconds=Decimal("55.23"),
        duration=Decimal("2.53304"),
    ),
    SilenceEvent(when=now, kind="start", seconds=Decimal("2216"), duration=None),
    SilenceEvent(
        when=now,
        kind="end",
        seconds=Decimal("2218.73"),
        duration=Decimal("2.73506"),
    ),
    SilenceEvent(when=now, kind="start", seconds=Decimal("2421.39"), duration=None),
    SilenceEvent(
        when=now,
        kind="end",
        seconds=Decimal("2423.92"),
        duration=Decimal("2.53304"),
    ),
]


@patch("earhorn.event.now")
def test_parse_silence_detect(now_mock: Mock):
    now_mock.return_value = now
    for line, expected in zip(
        SILENCE_DETECT_RAW.strip().splitlines(),
        SILENCE_DETECT_EVENTS,
    ):
        found = parse_silence_detect(line)
        assert found == expected


@patch("earhorn.event.now")
def test_silence_handler(now_mock: Mock):
    now_mock.return_value = now

    sample_events = [
        SilenceEvent(
            name="silence",
            kind="start",
            seconds=Decimal("5.00338"),
            duration=None,
        ),
        SilenceEvent(
            name="silence",
            kind="end",
            seconds=Decimal("9.99696"),
            duration=Decimal("4.99358"),
        ),
        SilenceEvent(
            name="silence",
            kind="start",
            seconds=Decimal("15.0027"),
            duration=None,
        ),
        SilenceEvent(
            name="silence",
            kind="end",
            seconds=Decimal("20.0061"),
            duration=Decimal("5.00338"),
        ),
    ]

    stop = ThreadEvent()
    queue: Queue[SilenceEvent] = Queue()
    stream_listener = StreamListener(
        stop=stop,
        event_queue=queue,
        stream_url=str(here / "sample.ogg"),
        handlers=[SilenceHandler(stop=stop, event_queue=queue)],
    )
    stream_listener.listen()
    stop.set()

    for expected in sample_events:
        found = queue.get(False)
        assert found.name == expected.name
        assert found.kind == expected.kind
        assert found.seconds == pytest.approx(expected.seconds, rel=1e-3)
        assert found.duration == pytest.approx(expected.duration, rel=1e-3)

    assert queue.empty()
