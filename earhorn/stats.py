from threading import Event as ThreadEvent
from threading import Thread
from time import sleep
from typing import Dict, Tuple

import httpx
from loguru import logger
from lxml import etree
from prometheus_client import Gauge

from .prometheus import (
    icecast,
    icecast_client_connections,
    icecast_clients,
    icecast_connections,
    icecast_file_connections,
    icecast_listener_connections,
    icecast_listeners,
    icecast_source,
    icecast_source_client_connections,
    icecast_source_listener_peak,
    icecast_source_listeners,
    icecast_source_relay_connections,
    icecast_source_slow_listeners,
    icecast_source_total_bytes_read,
    icecast_source_total_bytes_sent,
    icecast_source_total_connections,
    icecast_sources,
    icecast_stats,
    icecast_stats_connections,
    stats_extraction,
)


def set_gauge_factory(metric: Gauge):
    def func(element: etree._Element):
        if element.text is not None:
            metric.set(int(element.text))

    return func


def set_gauge_labels_factory(metric: Gauge):
    def func(element: etree._Element, labels: Dict[str, str]):
        if element.text is not None:
            metric.labels(**labels).set(int(element.text))

    return func


ICECAST_SOURCE_MAPPING = {
    "listener_peak": set_gauge_labels_factory(icecast_source_listener_peak),
    "listeners": set_gauge_labels_factory(icecast_source_listeners),
    "slow_listeners": set_gauge_labels_factory(icecast_source_slow_listeners),
    "total_bytes_read": set_gauge_labels_factory(icecast_source_total_bytes_read),
    "total_bytes_sent": set_gauge_labels_factory(icecast_source_total_bytes_sent),
}

ICECAST_SOURCE_INFO_LIST = {
    "server_name",
    "server_description",
    "server_type",
    "audio_info",
    "user_agent",
    "stream_start_iso8601",
}


def extract_icecast_source_stats(element: etree._Element):
    infos: Dict[str, str] = {}
    labels = {"mount": element.attrib.get("mount")}

    for child in element.iterchildren():
        if child.tag in ICECAST_SOURCE_INFO_LIST:
            if child.text is not None:
                infos[child.tag] = child.text

        elif child.tag in ICECAST_SOURCE_MAPPING:
            ICECAST_SOURCE_MAPPING[child.tag](child, labels)

    icecast_source.labels(**labels).info(infos)


ICECAST_MAPPING = {
    "client_connections": set_gauge_factory(icecast_client_connections),
    "clients": set_gauge_factory(icecast_clients),
    "connections": set_gauge_factory(icecast_connections),
    "file_connections": set_gauge_factory(icecast_file_connections),
    "listener_connections": set_gauge_factory(icecast_listener_connections),
    "listeners": set_gauge_factory(icecast_listeners),
    "source_client_connections": set_gauge_factory(icecast_source_client_connections),
    "source_relay_connections": set_gauge_factory(icecast_source_relay_connections),
    "source_total_connections": set_gauge_factory(icecast_source_total_connections),
    "sources": set_gauge_factory(icecast_sources),
    "stats": set_gauge_factory(icecast_stats),
    "stats_connections": set_gauge_factory(icecast_stats_connections),
    "source": extract_icecast_source_stats,
}

ICECAST_INFO_LIST = {
    "admin",
    "host",
    "location",
    "server_id",
    "server_start_iso8601",
}


def extract_icecast_stats(element: etree._Element):
    infos: Dict[str, str] = {}
    for child in element.iterchildren():
        if child.tag in ICECAST_INFO_LIST:
            if child.text is not None:
                infos[child.tag] = child.text

        elif child.tag in ICECAST_MAPPING:
            ICECAST_MAPPING[child.tag](child)

    icecast.info(infos)


@stats_extraction.time()
def extract_xml_stats(blob: str):
    element = etree.fromstring(blob)
    extract_icecast_stats(element)


class StatsExporter(Thread):
    name = "stats_exporter"
    stop: ThreadEvent
    url: str
    auth: Tuple[str, str]
    rate: int

    def __init__(
        self,
        stop: ThreadEvent,
        url: str,
        auth: Tuple[str, str],
        rate: int = 15,
    ):
        Thread.__init__(self)
        self.stop = stop
        self.url = url
        self.auth = auth
        self.rate = rate

    def run(self):
        logger.info(f"starting stats exporter with a {self.rate}s refresh rate ")

        while not self.stop.is_set():
            try:
                logger.trace(f"fetching stats from '{self.url}'")
                response = httpx.get(self.url, auth=self.auth)
                response.raise_for_status()
                extract_xml_stats(response.text)

            except (
                httpx.ConnectError,
                httpx.HTTPStatusError,
                httpx.ReadTimeout,
            ) as error:
                logger.error(f"could not get stats from '{self.url}'")
                logger.debug(error)

            if not self.stop.is_set():
                sleep(self.rate)

        logger.info("stats exporter stopped")
