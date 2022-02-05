from prometheus_client import Enum

stream_status = Enum(
    "stream_status",
    "Whether the stream is up",
    states=["up", "down"],
)
stream_silence = Enum(
    "stream_silence",
    "Whether the stream is silent",
    states=["up", "down"],
)
