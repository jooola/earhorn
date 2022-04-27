from prometheus_client import Enum, Summary

# Internal

stats_scraping = Summary(
    "earhorn_stats_scraping",
    "Time spent extracting Icecast stats",
)

# Stream

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
