from threading import Event as ThreadEvent
from threading import Thread
from time import sleep
from typing import Any, Tuple

import httpx
from loguru import logger
from lxml import etree

from .prometheus import (
    icecast_client_connections,
    icecast_clients,
    icecast_connections,
    icecast_file_connections,
    icecast_listener_connections,
    icecast_listeners,
    icecast_server,
    icecast_source_client_connections,
    icecast_source_relay_connections,
    icecast_source_total_connections,
    icecast_sources,
    icecast_sources_listener_peak,
    icecast_sources_listeners,
    icecast_sources_slow_listeners,
    icecast_sources_total_bytes_read,
    icecast_sources_total_bytes_sent,
    stats_extraction_seconds,
)


def must_find(root, key: str) -> Any:
    node = root.find(key)
    if node is None:
        raise Exception(f"could not find '{key}' in stats!")

    return node


def must_find_text(root, key: str) -> str:
    value = must_find(root, key).text
    if value is None:
        raise Exception(f"could not find '{key}' value in stats!")

    return value


def must_find_int(root, key: str) -> int:
    return int(must_find_text(root, key))


@stats_extraction_seconds.time()
def extract_xml_stats(blob: str):
    """
    See https://www.icecast.org/docs/icecast-2.4.1/server-stats.html for
    details about available icecast stats.
    """
    root = etree.fromstring(blob)

    icecast_server.info(
        {
            "server_id": must_find_text(root, "server_id"),
            "server_start": must_find_text(root, "server_start_iso8601"),
        }
    )

    icecast_clients.set(
        must_find_int(root, "clients"),
    )
    icecast_client_connections.set(
        must_find_int(root, "client_connections"),
    )
    icecast_listeners.set(
        must_find_int(root, "listeners"),
    )
    icecast_listener_connections.set(
        must_find_int(root, "listener_connections"),
    )
    icecast_file_connections.set(
        must_find_int(root, "file_connections"),
    )
    icecast_connections.set(
        must_find_int(root, "connections"),
    )
    icecast_source_client_connections.set(
        must_find_int(root, "source_client_connections"),
    )
    icecast_source_relay_connections.set(
        must_find_int(root, "source_relay_connections"),
    )
    icecast_source_total_connections.set(
        must_find_int(root, "source_total_connections"),
    )

    for source in root.iterfind("source"):
        mount = source.attrib.get("mount")

        icecast_sources.labels(mount=mount).info(
            {
                "stream_start": must_find_text(source, "stream_start_iso8601"),
                "audio_info": must_find_text(source, "audio_info"),
                "source_ip": must_find_text(source, "source_ip"),
                "user_agent": must_find_text(source, "user_agent"),
            }
        )

        icecast_sources_listener_peak.labels(mount=mount).set(
            must_find_int(source, "listener_peak")
        )
        icecast_sources_listeners.labels(mount=mount).set(
            must_find_int(source, "listeners")
        )
        icecast_sources_slow_listeners.labels(mount=mount).set(
            must_find_int(source, "slow_listeners")
        )
        icecast_sources_total_bytes_read.labels(mount=mount).set(
            must_find_int(source, "total_bytes_read")
        )
        icecast_sources_total_bytes_sent.labels(mount=mount).set(
            must_find_int(source, "total_bytes_sent")
        )


class StatsHandler(Thread):
    name = "stats_handler"
    stop: ThreadEvent
    url: str
    auth: Tuple[str, str]

    def __init__(self, stop: ThreadEvent, url: str, auth: Tuple[str, str]):
        Thread.__init__(self)
        self.stop = stop
        self.url = url
        self.auth = auth

    def run(self):
        logger.info("starting stats handler")

        while not self.stop.is_set():
            try:
                response = httpx.get(self.url, auth=self.auth)
                response.raise_for_status()
                extract_xml_stats(response.text)

            except (httpx.ConnectError, httpx.HTTPStatusError) as error:
                logger.error(f"could not get stats from '{self.url}'")
                logger.debug(error)
                sleep(5)

        logger.info("stats handler stopped")
