from prometheus_client import Enum

stream_status = Enum(
    "earhorn_stream_status",
    "Whether the stream is up",
    states=["up", "down"],
)
stream_silence = Enum(
    "earhorn_stream_silence",
    "Whether the stream is silent",
    states=["up", "down"],
)
