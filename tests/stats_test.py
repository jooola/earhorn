# pylint: disable=line-too-long

from pathlib import Path

from prometheus_client import REGISTRY, generate_latest

from earhorn.stats import extract_xml_stats

here = Path(__file__).parent


def generate_restricted(key):
    blob = generate_latest(REGISTRY.restricted_registry([key]))
    return blob.decode(encoding="utf-8").splitlines()


def test_extract_xml_stats():
    stats_filepath = here / "stats.xml"
    blob = stats_filepath.read_text(encoding="utf-8")
    extract_xml_stats(blob)

    assert generate_restricted("icecast_server_info") == [
        "# HELP icecast_server_info Icecast server info",
        "# TYPE icecast_server_info gauge",
        'icecast_server_info{server_id="Icecast 2.4.4",server_start="2022-03-15T18:29:12+0100"} 1.0',
    ]
    assert generate_restricted("icecast_clients") == [
        "# HELP icecast_clients Icecast clients",
        "# TYPE icecast_clients gauge",
        "icecast_clients 7.0",
    ]
    assert generate_restricted("icecast_client_connections") == [
        "# HELP icecast_client_connections Icecast client connections",
        "# TYPE icecast_client_connections gauge",
        "icecast_client_connections 3935.0",
    ]
    assert generate_restricted("icecast_listeners") == [
        "# HELP icecast_listeners Icecast listeners",
        "# TYPE icecast_listeners gauge",
        "icecast_listeners 5.0",
    ]
    assert generate_restricted("icecast_listener_connections") == [
        "# HELP icecast_listener_connections Icecast listener connections",
        "# TYPE icecast_listener_connections gauge",
        "icecast_listener_connections 117.0",
    ]
    assert generate_restricted("icecast_file_connections") == [
        "# HELP icecast_file_connections Icecast file connections",
        "# TYPE icecast_file_connections gauge",
        "icecast_file_connections 14.0",
    ]
    assert generate_restricted("icecast_connections") == [
        "# HELP icecast_connections Icecast connections",
        "# TYPE icecast_connections gauge",
        "icecast_connections 4201.0",
    ]
    assert generate_restricted("icecast_source_client_connections") == [
        "# HELP icecast_source_client_connections Icecast source client connections",
        "# TYPE icecast_source_client_connections gauge",
        "icecast_source_client_connections 2.0",
    ]
    assert generate_restricted("icecast_source_relay_connections") == [
        "# HELP icecast_source_relay_connections Icecast source relay connections",
        "# TYPE icecast_source_relay_connections gauge",
        "icecast_source_relay_connections 0.0",
    ]
    assert generate_restricted("icecast_source_total_connections") == [
        "# HELP icecast_source_total_connections Icecast source total connections",
        "# TYPE icecast_source_total_connections gauge",
        "icecast_source_total_connections 2.0",
    ]
    assert generate_restricted("icecast_sources_info") == [
        "# HELP icecast_sources_info Icecast sources info",
        "# TYPE icecast_sources_info gauge",
        'icecast_sources_info{audio_info="channels=2;samplerate=44100;bitrate=320",mount="/main.mp3",source_ip="192.168.100.20",stream_start="2022-03-15T18:29:19+0100",user_agent="Liquidsoap/1.4.4 (Unix; OCaml 4.10.0)"} 1.0',
        'icecast_sources_info{audio_info="channels=2;quality=0.8;samplerate=44100",mount="/main.ogg",source_ip="192.168.100.20",stream_start="2022-03-15T18:29:19+0100",user_agent="Liquidsoap/1.4.4 (Unix; OCaml 4.10.0)"} 1.0',
    ]
    assert generate_restricted("icecast_sources_listener_peak") == [
        "# HELP icecast_sources_listener_peak Icecast sources listener peak",
        "# TYPE icecast_sources_listener_peak gauge",
        'icecast_sources_listener_peak{mount="/main.mp3"} 7.0',
        'icecast_sources_listener_peak{mount="/main.ogg"} 4.0',
    ]
    assert generate_restricted("icecast_sources_listeners") == [
        "# HELP icecast_sources_listeners Icecast sources listeners",
        "# TYPE icecast_sources_listeners gauge",
        'icecast_sources_listeners{mount="/main.mp3"} 3.0',
        'icecast_sources_listeners{mount="/main.ogg"} 2.0',
    ]
    assert generate_restricted("icecast_sources_slow_listeners") == [
        "# HELP icecast_sources_slow_listeners Icecast sources slow listeners",
        "# TYPE icecast_sources_slow_listeners gauge",
        'icecast_sources_slow_listeners{mount="/main.mp3"} 2.0',
        'icecast_sources_slow_listeners{mount="/main.ogg"} 2.0',
    ]
    assert generate_restricted("icecast_sources_total_bytes_read") == [
        "# HELP icecast_sources_total_bytes_read Icecast sources total bytes read",
        "# TYPE icecast_sources_total_bytes_read gauge",
        'icecast_sources_total_bytes_read{mount="/main.mp3"} 6.1103882e+09',
        'icecast_sources_total_bytes_read{mount="/main.ogg"} 4.499297657e+09',
    ]
    assert generate_restricted("icecast_sources_total_bytes_sent") == [
        "# HELP icecast_sources_total_bytes_sent Icecast sources total bytes send",
        "# TYPE icecast_sources_total_bytes_sent gauge",
        'icecast_sources_total_bytes_sent{mount="/main.mp3"} 2.0338244727e+010',
        'icecast_sources_total_bytes_sent{mount="/main.ogg"} 9.051758982e+09',
    ]
