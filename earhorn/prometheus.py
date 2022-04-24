from prometheus_client import Enum, Gauge, Info, Summary

# Internal

stats_extraction = Summary(
    "earhorn_stats_extraction",
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

# Icecast server
# https://icecast.org/docs/icecast-latest/server-stats.html

icecast = Info(
    "icecast",
    "Details usually set in the server config, such as: admin, host, "
    "location, server_id, server_start_iso8601.",
)

icecast_client_connections = Gauge(
    "icecast_client_connections",
    "Client connections are basically anything that is not a source "
    "connection. These include listeners (not concurrent, but cumulative), "
    "any admin function accesses, and any static content (file serving) "
    "accesses. This is an accumulating counter.",
)
icecast_clients = Gauge(
    "icecast_clients",
    "Number of currently active client connections.",
)
icecast_connections = Gauge(
    "icecast_connections",
    "The total of all inbound TCP connections since start-up. "
    "This is an accumulating counter.",
)
icecast_file_connections = Gauge(
    "icecast_file_connections",
    "This is an accumulating counter.",
)
icecast_listener_connections = Gauge(
    "icecast_listener_connections",
    "Number of listener connections to mount points. "
    "This is an accumulating counter.",
)
icecast_listeners = Gauge(
    "icecast_listeners", "Number of currently active listener connections."
)
icecast_source_client_connections = Gauge(
    "icecast_source_client_connections",
    "Source client connections are the number of times (cumulative since "
    "start-up, not just currently connected) a source client has connected "
    "to Icecast. This is an accumulating counter.",
)
icecast_source_relay_connections = Gauge(
    "icecast_source_relay_connections",
    "Number of outbound relay connections to (master) icecast servers. "
    "This is an accumulating counter.",
)
icecast_source_total_connections = Gauge(
    "icecast_source_total_connections",
    "Both clients and relays. This is an accumulating counter.",
)
icecast_sources = Gauge(
    "icecast_sources",
    "The total of currently connected sources.",
)
icecast_stats = Gauge(
    "icecast_stats",
    "The total of currently connected STATS clients.",
)
icecast_stats_connections = Gauge(
    "icecast_stats_connections",
    "Number of times a stats client has connected to Icecast. "
    "This is an accumulating counter.",
)

# Icecast sources

icecast_source = Info(
    "icecast_source",
    "Details for the Icecast source, such as: server_name, "
    "server_description, server_type, audio_info, user_agent, "
    "stream_start_iso8601, max_listeners.",
    ["mount"],
)

icecast_source_listener_peak = Gauge(
    "icecast_source_listener_peak",
    "Peak concurrent number of listener connections for this mountpoint.",
    ["mount"],
)
icecast_source_listeners = Gauge(
    "icecast_source_listeners",
    "The number of currently connected listeners.",
    ["mount"],
)
icecast_source_slow_listeners = Gauge(
    "icecast_source_slow_listeners",
    "Number of slow listeners.",
    ["mount"],
)
icecast_source_total_bytes_read = Gauge(
    "icecast_source_total_bytes_read",
    "Total number of bytes received from the source client.",
    ["mount"],
)
icecast_source_total_bytes_sent = Gauge(
    "icecast_source_total_bytes_sent",
    "Total number of bytes sent to all listener connections since "
    "last source connect.",
    ["mount"],
)
