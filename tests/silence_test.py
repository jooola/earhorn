from datetime import datetime
from unittest import mock

from more_itertools import grouper
from pytest import mark

from earhorn.silence import (
    SilenceEvent,
    parse_silence_detect,
    validate_silence_duration,
)

SILENCE_DETECT_RAW = """
[silencedetect @ 0x559578eea680] silence_start: 52.697
[silencedetect @ 0x559578eea680] silence_end: 55.23 | silence_duration: 2.53304
[silencedetect @ 0x55ef37b94c80] silence_start: 2216
[silencedetect @ 0x55ef37b94c80] silence_end: 2218.73 | silence_duration: 2.73506
[silencedetect @ 0x55ef37b94c80] silence_start: 2421.39
[silencedetect @ 0x55ef37b94c80] silence_end: 2423.92 | silence_duration: 2.53304
"""

now = datetime.now()

SILENCE_DETECT_EVENTS = [
    SilenceEvent(now, "start", 52.697, None),
    SilenceEvent(now, "end", 55.23, 2.53304),
    SilenceEvent(now, "start", 2216, None),
    SilenceEvent(now, "end", 2218.73, 2.73506),
    SilenceEvent(now, "start", 2421.39, None),
    SilenceEvent(now, "end", 2423.92, 2.53304),
]


def test_parse_silence_detect():
    with mock.patch("earhorn.silence.now") as now_mock:
        now_mock.return_value = now

        for line, expected in zip(
            SILENCE_DETECT_RAW.strip().splitlines(),
            SILENCE_DETECT_EVENTS,
        ):
            assert parse_silence_detect(line) == expected


@mark.parametrize(
    "start,end",
    grouper(SILENCE_DETECT_EVENTS, 2),
)
def test_validate_silence_duration(start, end):
    assert validate_silence_duration(start, end)
