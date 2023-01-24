from prometheus_client import Counter, Enum, Summary

# Internal

stats_scraping = Summary(
    "earhorn_stats_scraping",
    "Time spent extracting Icecast stats",
)

stats_errors = Counter(
    "earhorn_stats_errors",
    "Errors count extracting Icecast stats",
)

# Archive

archive_segments = Counter(
    "earhorn_archive_segments",
    "Archiver segments counter",
    labelnames=["state"],
)

archive_errors = Counter(
    "earhorn_archive_errors",
    "Archiver errors counter",
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
