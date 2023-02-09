import json
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import pytest

from earhorn.event import FileHook, HookError, SilenceEvent

here = Path(__file__).parent


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


@pytest.fixture(name="file_hook_event")
def fixture_file_hook_event():
    return SilenceEvent(
        when=datetime(2022, 8, 16, 19, 1, 36, 791399),
        kind="start",
        seconds=Decimal("0"),
    )


def test_file_hook(file_hook_event: SilenceEvent):
    hook = FileHook(str(here / "event_hook.sh"))
    hook(file_hook_event)


def test_file_hook_failure(file_hook_event: SilenceEvent):
    hook = FileHook(str(here / "event_hook.sh"))
    file_hook_event.kind = "invalid"  # type: ignore[assignment]
    with pytest.raises(HookError):
        hook(file_hook_event)


def test_file_hook_must_exists():
    with pytest.raises(ValueError):
        FileHook(str(here / "inexistent.sh"))
