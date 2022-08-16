import json
from datetime import datetime
from decimal import Decimal

from earhorn.event import SilenceEvent


def test_event_json():
    assert SilenceEvent(
        when=datetime(2022, 8, 16, 19, 1, 36, 791399),
        kind="start",
        seconds=Decimal("0"),
    ).json() == json.dumps(
        {
            "when": "2022-08-16T19:01:36.791399",
            "kind": "start",
            "seconds": 0,
            "duration": None,
            "name": "silence",
        }
    )
    assert SilenceEvent(
        when=datetime(2022, 8, 16, 19, 1, 39, 361082),
        kind="end",
        seconds=Decimal("4.57095"),
        duration=Decimal("4.57095"),
    ).json() == json.dumps(
        {
            "when": "2022-08-16T19:01:39.361082",
            "kind": "end",
            "seconds": 4.57095,
            "duration": 4.57095,
            "name": "silence",
        }
    )
