#!/usr/bin/env python

# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import datetime
import logging
import os
import subprocess
import typing as t
from wsgiref import simple_server

import prometheus_client
import psutil

METRICS_PORT = int(os.getenv("METRICS_PORT", "9118"))
LOGGER = logging.getLogger(__file__)
IDLETIME = prometheus_client.Gauge(
    "idletime_minutes", "Idletime of X server in minutes from xprintidle"
)


class IdleTimer:
    """Measure the idle time of the X server even if there is no X server."""

    def __init__(self) -> None:
        now = datetime.datetime.now()
        self.first_checkpoint = (now, self._xprintidle(init=True) or -1.0)
        self.last_checkpoint = self.first_checkpoint

    def _xprintidle(self, *, init: bool = False) -> float:
        proc = subprocess.run(
            ["xprintidle"], check=False, capture_output=True, encoding="utf-8"
        )
        LOGGER.debug("xprintidle's stdout: '%s'", proc.stdout)
        LOGGER.debug("xprintidle's stderr: '%r'", proc.stderr)
        if proc.stdout in {"couldn't open display", ""}:
            if init or self.last_checkpoint[1] == -1.0:
                LOGGER.debug("no display on init")
                return -1.0

            checkpoint, idle_time = self.last_checkpoint
            delta = datetime.datetime.now() - checkpoint
            return (delta + datetime.timedelta(seconds=idle_time)).seconds

        return float(proc.stdout) / 60000

    def get_idletime(self) -> float:
        """Return idle time in minutes.

        If there is an X server return output of xprintidle (Idle time
        of X server in millisecs) in minutes. If there is no display the
        idle time increases. Then the timedelta from now and the last
        successfull xprintidle exec is returned.
        """
        current_idle_time = self._xprintidle()
        self.last_checkpoint = (datetime.datetime.now(), current_idle_time)
        return round(current_idle_time, 2)


class ProcessCollector(prometheus_client.registry.Collector):
    """Track metrics of all system processes."""

    def collect(self) -> t.Iterable[prometheus_client.Metric]:
        """Collect metrics from all system processes."""
        processes = psutil.process_iter()

        process_cpu_percent_metric = (
            prometheus_client.metrics_core.GaugeMetricFamily(
                "process_cpu_percent",
                "CPU percent of the process",
                labels=["process_name"],
            )
        )

        process_memory_usage_metric = (
            prometheus_client.metrics_core.GaugeMetricFamily(
                "process_memory_usage_bytes",
                "Memory usage of the process in bytes",
                labels=["process_name"],
            )
        )

        process_io_counters_metric = (
            prometheus_client.metrics_core.GaugeMetricFamily(
                "process_io_counters_bytes",
                "Read and write bytes by the process",
                labels=["process_name", "io_type"],
            )
        )

        process_num_threads_metric = (
            prometheus_client.metrics_core.GaugeMetricFamily(
                "process_num_threads",
                "Number of threads of the process",
                labels=["process_name"],
            )
        )

        process_open_fds_metric = (
            prometheus_client.metrics_core.GaugeMetricFamily(
                "process_open_file_descriptors",
                "Number of open file descriptors by the process",
                labels=["process_name"],
            )
        )

        for process in processes:
            with process.oneshot():
                process_cpu_percent_metric.add_metric(
                    [process.name()], process.cpu_percent()
                )

                process_memory_usage_metric.add_metric(
                    [process.name()], process.memory_info().rss
                )

                io_counters = process.io_counters()
                if io_counters:
                    process_io_counters_metric.add_metric(
                        [process.name(), "read"], io_counters.read_bytes
                    )
                    process_io_counters_metric.add_metric(
                        [process.name(), "write"], io_counters.write_bytes
                    )

                process_num_threads_metric.add_metric(
                    [process.name()], process.num_threads()
                )

                if hasattr(process, "num_fds"):
                    process_open_fds_metric.add_metric(
                        [process.name()], process.num_fds()
                    )

        yield process_cpu_percent_metric
        yield process_memory_usage_metric
        yield process_io_counters_metric
        yield process_num_threads_metric
        yield process_open_fds_metric


IDLETIME.set_function(IdleTimer().get_idletime)

prometheus_client.REGISTRY.register(ProcessCollector())


def start_server(
    addr: str,
    port: int,
    registry: prometheus_client.registry.CollectorRegistry,
) -> None:
    """Start a WSGI server for Prometheus metrics on the main thread."""
    app = prometheus_client.make_wsgi_app(registry)
    httpd = simple_server.make_server(addr, port, app)
    httpd.serve_forever()


if __name__ == "__main__":
    start_server(
        addr="", port=METRICS_PORT, registry=prometheus_client.REGISTRY
    )
