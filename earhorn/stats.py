from typing import Dict, Tuple

import httpx
from loguru import logger
from lxml import etree
from prometheus_client.core import (
    REGISTRY,
    CollectorRegistry,
    GaugeMetricFamily,
    InfoMetricFamily,
)

from .prometheus import stats_scraping

ICECAST_SOURCE_INFO_KEYS = {
    "server_name",
    "server_description",
    "server_type",
    "audio_info",
    "user_agent",
    "stream_start_iso8601",
}

ICECAST_INFO_KEYS = {
    "admin",
    "host",
    "location",
    "server_id",
    "server_start_iso8601",
}


def gauge_metric_family_with_labels(
    name: str,
    documentation: str,
    value: str,
    labels: Dict[str, str],
):
    metric = GaugeMetricFamily(
        name=name,
        documentation=documentation,
        labels=list(labels.keys()),
    )
    metric.add_metric(
        list(labels.values()),
        int(value),
    )
    return metric


def icecast_metrics_factory():
    return InfoMetricFamily(
        name="icecast",
        documentation="Details usually set in the server config, such as: admin, host, "
        "location, server_id, server_start_iso8601.",
    ), {
        "client_connections": GaugeMetricFamily(
            name="icecast_client_connections",
            documentation="Client connections are basically anything that is not a source "
            "connection. These include listeners (not concurrent, but cumulative), "
            "any admin function accesses, and any static content (file serving) "
            "accesses. This is an accumulating counter.",
        ),
        "clients": GaugeMetricFamily(
            name="icecast_clients",
            documentation="Number of currently active client connections.",
        ),
        "connections": GaugeMetricFamily(
            name="icecast_connections",
            documentation="The total of all inbound TCP connections since start-up. "
            "This is an accumulating counter.",
        ),
        "file_connections": GaugeMetricFamily(
            name="icecast_file_connections",
            documentation="This is an accumulating counter.",
        ),
        "listener_connections": GaugeMetricFamily(
            name="icecast_listener_connections",
            documentation="Number of listener connections to mount points. "
            "This is an accumulating counter.",
        ),
        "listeners": GaugeMetricFamily(
            name="icecast_listeners",
            documentation="Number of currently active listener connections.",
        ),
        "source_client_connections": GaugeMetricFamily(
            name="icecast_source_client_connections",
            documentation="Source client connections are the number of times (cumulative since "
            "start-up, not just currently connected) a source client has connected "
            "to Icecast. This is an accumulating counter.",
        ),
        "source_relay_connections": GaugeMetricFamily(
            name="icecast_source_relay_connections",
            documentation="Number of outbound relay connections to (master) icecast servers. "
            "This is an accumulating counter.",
        ),
        "source_total_connections": GaugeMetricFamily(
            name="icecast_source_total_connections",
            documentation="Both clients and relays. This is an accumulating counter.",
        ),
        "sources": GaugeMetricFamily(
            name="icecast_sources",
            documentation="The total of currently connected sources.",
        ),
        "stats": GaugeMetricFamily(
            name="icecast_stats",
            documentation="The total of currently connected STATS clients.",
        ),
        "stats_connections": GaugeMetricFamily(
            name="icecast_stats_connections",
            documentation="Number of times a stats client has connected to Icecast. "
            "This is an accumulating counter.",
        ),
    }


def icecast_source_metrics_factory():
    return InfoMetricFamily(
        name="icecast_source",
        documentation="Details for the Icecast source, such as: server_name, "
        "server_description, server_type, audio_info, user_agent, "
        "stream_start_iso8601, max_listeners.",
        labels=["mount"],
    ), {
        "listener_peak": GaugeMetricFamily(
            name="icecast_source_listener_peak",
            documentation="Peak concurrent number of listener connections for this mountpoint.",
            labels=["mount"],
        ),
        "listeners": GaugeMetricFamily(
            name="icecast_source_listeners",
            documentation="The number of currently connected listeners.",
            labels=["mount"],
        ),
        "slow_listeners": GaugeMetricFamily(
            name="icecast_source_slow_listeners",
            documentation="Number of slow listeners.",
            labels=["mount"],
        ),
        "total_bytes_read": GaugeMetricFamily(
            name="icecast_source_total_bytes_read",
            documentation="Total number of bytes received from the source client.",
            labels=["mount"],
        ),
        "total_bytes_sent": GaugeMetricFamily(
            name="icecast_source_total_bytes_sent",
            documentation="Total number of bytes sent to all listener connections since "
            "last source connect.",
            labels=["mount"],
        ),
    }


# pylint: disable=too-few-public-methods
class StatsCollector:
    """
    Collect and forward stats defined in
    https://icecast.org/docs/icecast-latest/server-stats.html
    """

    _client: httpx.Client
    url: str
    auth: Tuple[str, str]

    def __init__(
        self,
        url: str,
        auth: Tuple[str, str],
        registry: CollectorRegistry = REGISTRY,
    ):
        self.url = url
        self.auth = auth
        self._client = httpx.Client()

        if registry:
            logger.debug("registering stats collector")
            registry.register(self)  # type: ignore

    def close(self):
        logger.debug("closing stats collector")
        self._client.close()

    @stats_scraping.time()
    def collect(self):
        logger.trace(f"collecting stats from '{self.url}'")
        try:
            response = self._client.get(self.url, auth=self.auth)
            response.raise_for_status()

        except (
            httpx.ConnectError,
            httpx.HTTPStatusError,
            httpx.ReadError,
            httpx.ReadTimeout,
        ) as error:
            logger.error(error)
            return []

        root = etree.fromstring(response.text)

        icecast_info, icecast_metrics = icecast_metrics_factory()
        icecast_source_info, icecast_source_metrics = icecast_source_metrics_factory()

        metrics = []
        metrics.append(icecast_info)
        metrics.extend(icecast_metrics.values())
        metrics.append(icecast_source_info)
        metrics.extend(icecast_source_metrics.values())

        infos: Dict[str, str] = {}
        for child in root.iterchildren():
            if child.tag in ICECAST_INFO_KEYS:
                if child.text is not None:
                    infos[child.tag] = child.text

            elif child.tag in icecast_metrics:
                if child.text is not None:
                    icecast_metrics[child.tag].add_metric(
                        [],
                        int(child.text),
                    )

            elif child.tag == "source":
                source_infos: Dict[str, str] = {}
                source_labels = [child.attrib.get("mount")]

                for source_child in child.iterchildren():
                    if source_child.tag in ICECAST_SOURCE_INFO_KEYS:
                        if source_child.text is not None:
                            source_infos[source_child.tag] = source_child.text

                    if source_child.tag in icecast_source_metrics:
                        if source_child.text is not None:
                            icecast_source_metrics[source_child.tag].add_metric(
                                source_labels,
                                int(source_child.text),
                            )

                icecast_source_info.add_metric(source_labels, source_infos)
        icecast_info.add_metric([], infos)

        return metrics
