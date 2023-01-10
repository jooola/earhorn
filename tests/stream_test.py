from datetime import datetime
from pathlib import Path
from queue import Queue
from threading import Event as ThreadEvent
from unittest.mock import patch

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
    SilenceEvent(when=now, kind="start", seconds=52.697, duration=None),
    SilenceEvent(when=now, kind="end", seconds=55.23, duration=2.53304),
    SilenceEvent(when=now, kind="start", seconds=2216, duration=None),
    SilenceEvent(when=now, kind="end", seconds=2218.73, duration=2.73506),
    SilenceEvent(when=now, kind="start", seconds=2421.39, duration=None),
    SilenceEvent(when=now, kind="end", seconds=2423.92, duration=2.53304),
]


def test_parse_silence_detect():
    with patch("earhorn.event.now") as now_mock:
        now_mock.return_value = now
        for line, expected in zip(
            SILENCE_DETECT_RAW.strip().splitlines(),
            SILENCE_DETECT_EVENTS,
        ):
            found = parse_silence_detect(line)
            assert found == expected


def test_silence_handler():
    with patch("earhorn.event.now") as now_mock:
        now_mock.return_value = now

        sample_events = [
            SilenceEvent(name="silence", kind="start", seconds=5.00338, duration=None),
            SilenceEvent(name="silence", kind="end", seconds=9.99696, duration=4.99358),
            SilenceEvent(name="silence", kind="start", seconds=15.0027, duration=None),
            SilenceEvent(name="silence", kind="end", seconds=20.0061, duration=5.00336),
        ]

        queue: Queue = Queue()
        stream_listener = StreamListener(
            stop=ThreadEvent(),
            event_queue=queue,
            stream_url=str(here / "sample.ogg"),
            handlers=[SilenceHandler(event_queue=queue)],
        )
        stream_listener.listen()

        for expected in sample_events:
            found = queue.get(False)
            assert found == expected

        assert queue.empty()
