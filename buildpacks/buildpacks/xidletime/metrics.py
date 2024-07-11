#!/usr/bin/env python

# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import datetime
import logging
import os
import subprocess
from wsgiref import simple_server

import prometheus_client

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


IDLETIME.set_function(IdleTimer().get_idletime)


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
