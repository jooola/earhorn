from prometheus_client import Enum, Gauge, Info

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

icecast_server = Info(
    "icecast_server",
    "Icecast server info",
)

icecast_clients = Gauge(
    "icecast_clients",
    "Icecast clients",
)
icecast_client_connections = Gauge(
    "icecast_client_connections",
    "Icecast client connections",
)

icecast_listeners = Gauge(
    "icecast_listeners",
    "Icecast listeners",
)
icecast_listener_connections = Gauge(
    "icecast_listener_connections",
    "Icecast listener connections",
)

icecast_file_connections = Gauge(
    "icecast_file_connections",
    "Icecast file connections",
)
icecast_connections = Gauge(
    "icecast_connections",
    "Icecast connections",
)

icecast_source_client_connections = Gauge(
    "icecast_source_client_connections",
    "Icecast source client connections",
)
icecast_source_relay_connections = Gauge(
    "icecast_source_relay_connections",
    "Icecast source relay connections",
)
icecast_source_total_connections = Gauge(
    "icecast_source_total_connections",
    "Icecast source total connections",
)

# Icecast sources

icecast_sources = Info(
    "icecast_sources",
    "Icecast sources info",
    ["mount"],
)

icecast_sources_listener_peak = Gauge(
    "icecast_sources_listener_peak",
    "Icecast sources listener peak",
    ["mount"],
)
icecast_sources_listeners = Gauge(
    "icecast_sources_listeners",
    "Icecast sources listeners",
    ["mount"],
)
icecast_sources_slow_listeners = Gauge(
    "icecast_sources_slow_listeners",
    "Icecast sources slow listeners",
    ["mount"],
)
icecast_sources_total_bytes_read = Gauge(
    "icecast_sources_total_bytes_read",
    "Icecast sources total bytes read",
    ["mount"],
)
icecast_sources_total_bytes_sent = Gauge(
    "icecast_sources_total_bytes_sent",
    "Icecast sources total bytes send",
    ["mount"],
)
