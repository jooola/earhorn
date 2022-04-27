# pylint: disable=line-too-long
from pathlib import Path

from prometheus_client import CollectorRegistry, generate_latest
from pytest_httpx import HTTPXMock

from earhorn.stats import StatsCollector

here = Path(__file__).parent


def test_icecast_collector(benchmark, httpx_mock: HTTPXMock):
    stats_filepath = here / "stats.xml"
    stats_url = "http://example.com/admin/stats.xml"
    stats_auth = ("admin", "hackme")

    httpx_mock.add_response(url=stats_url, content=stats_filepath.read_bytes())

    registry = CollectorRegistry()
    StatsCollector(
        url=stats_url,
        auth=stats_auth,
        registry=registry,
    )

    benchmark(registry.collect)

    assert generate_latest(registry).decode(encoding="utf-8").splitlines() == [
        "# HELP icecast_info Details usually set in the server config, such as: admin, host, location, server_id, server_start_iso8601.",
        "# TYPE icecast_info gauge",
        'icecast_info{admin="icemaster@radio.org",host="localhost",location="Moon",server_id="Icecast 2.4.4",server_start_iso8601="2022-03-15T18:29:12+0100"} 1.0',
        "# HELP icecast_client_connections Client connections are basically anything that is not a source connection. These include listeners (not concurrent, but cumulative), any admin function accesses, and any static content (file serving) accesses. This is an accumulating counter.",
        "# TYPE icecast_client_connections gauge",
        "icecast_client_connections 3935.0",
        "# HELP icecast_clients Number of currently active client connections.",
        "# TYPE icecast_clients gauge",
        "icecast_clients 7.0",
        "# HELP icecast_connections The total of all inbound TCP connections since start-up. This is an accumulating counter.",
        "# TYPE icecast_connections gauge",
        "icecast_connections 4201.0",
        "# HELP icecast_file_connections This is an accumulating counter.",
        "# TYPE icecast_file_connections gauge",
        "icecast_file_connections 14.0",
        "# HELP icecast_listener_connections Number of listener connections to mount points. This is an accumulating counter.",
        "# TYPE icecast_listener_connections gauge",
        "icecast_listener_connections 117.0",
        "# HELP icecast_listeners Number of currently active listener connections.",
        "# TYPE icecast_listeners gauge",
        "icecast_listeners 5.0",
        "# HELP icecast_source_client_connections Source client connections are the number of times (cumulative since start-up, not just currently connected) a source client has connected to Icecast. This is an accumulating counter.",
        "# TYPE icecast_source_client_connections gauge",
        "icecast_source_client_connections 2.0",
        "# HELP icecast_source_relay_connections Number of outbound relay connections to (master) icecast servers. This is an accumulating counter.",
        "# TYPE icecast_source_relay_connections gauge",
        "icecast_source_relay_connections 0.0",
        "# HELP icecast_source_total_connections Both clients and relays. This is an accumulating counter.",
        "# TYPE icecast_source_total_connections gauge",
        "icecast_source_total_connections 2.0",
        "# HELP icecast_sources The total of currently connected sources.",
        "# TYPE icecast_sources gauge",
        "icecast_sources 2.0",
        "# HELP icecast_stats The total of currently connected STATS clients.",
        "# TYPE icecast_stats gauge",
        "icecast_stats 0.0",
        "# HELP icecast_stats_connections Number of times a stats client has connected to Icecast. This is an accumulating counter.",
        "# TYPE icecast_stats_connections gauge",
        "icecast_stats_connections 0.0",
        "# HELP icecast_source_info Details for the Icecast source, such as: server_name, server_description, server_type, audio_info, user_agent, stream_start_iso8601, max_listeners.",
        "# TYPE icecast_source_info gauge",
        'icecast_source_info{audio_info="channels=2;samplerate=44100;bitrate=320",mount="/main.mp3",server_description="Main (mp3 320kbps)",server_name="Radio",server_type="audio/mpeg",stream_start_iso8601="2022-03-15T18:29:19+0100",user_agent="Liquidsoap/1.4.4 (Unix; OCaml 4.10.0)"} 1.0',
        'icecast_source_info{audio_info="channels=2;quality=0.8;samplerate=44100",mount="/main.ogg",server_description="Main (ogg 256kbps)",server_name="Radio",server_type="application/ogg",stream_start_iso8601="2022-03-15T18:29:19+0100",user_agent="Liquidsoap/1.4.4 (Unix; OCaml 4.10.0)"} 1.0',
        "# HELP icecast_source_listener_peak Peak concurrent number of listener connections for this mountpoint.",
        "# TYPE icecast_source_listener_peak gauge",
        'icecast_source_listener_peak{mount="/main.mp3"} 7.0',
        'icecast_source_listener_peak{mount="/main.ogg"} 4.0',
        "# HELP icecast_source_listeners The number of currently connected listeners.",
        "# TYPE icecast_source_listeners gauge",
        'icecast_source_listeners{mount="/main.mp3"} 3.0',
        'icecast_source_listeners{mount="/main.ogg"} 2.0',
        "# HELP icecast_source_slow_listeners Number of slow listeners.",
        "# TYPE icecast_source_slow_listeners gauge",
        'icecast_source_slow_listeners{mount="/main.mp3"} 2.0',
        'icecast_source_slow_listeners{mount="/main.ogg"} 2.0',
        "# HELP icecast_source_total_bytes_read Total number of bytes received from the source client.",
        "# TYPE icecast_source_total_bytes_read gauge",
        'icecast_source_total_bytes_read{mount="/main.mp3"} 6.1103882e+09',
        'icecast_source_total_bytes_read{mount="/main.ogg"} 4.499297657e+09',
        "# HELP icecast_source_total_bytes_sent Total number of bytes sent to all listener connections since last source connect.",
        "# TYPE icecast_source_total_bytes_sent gauge",
        'icecast_source_total_bytes_sent{mount="/main.mp3"} 2.0338244727e+010',
        'icecast_source_total_bytes_sent{mount="/main.ogg"} 9.051758982e+09',
    ]
