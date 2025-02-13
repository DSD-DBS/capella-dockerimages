#!/usr/bin/env python

# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import datetime
import logging
import os
from wsgiref import simple_server

import prometheus_client
import requests

METRICS_PORT = int(os.getenv("METRICS_PORT", "9118"))
LOGGER = logging.getLogger(__file__)

IDLETIME = prometheus_client.Gauge(
    "idletime_minutes", "Idletime of the Jupyter server in minutes."
)

PORT = os.getenv("JUPYTER_PORT", "8888")
BASE_URL = os.getenv("JUPYTER_BASE_URL", "/")
BASE_URL = BASE_URL.removesuffix("/")


def get_last_activity() -> datetime.datetime | None:
    """Return the last activity from the JupyterLab status API."""

    response = requests.get(
        f"http://localhost:{PORT}{BASE_URL}/api/status", timeout=1
    )

    if response.status_code != 200:
        LOGGER.error(
            "Failed to get last activity: %s", response.content.decode()
        )
        return None

    return datetime.datetime.fromisoformat(response.json()["last_activity"])


def get_idletime() -> float:
    """Return idle time in minutes."""

    now = datetime.datetime.now(datetime.UTC)
    last_activity = get_last_activity()

    if last_activity is None:
        return -1

    idletime = (now - last_activity).seconds / 60
    return round(idletime, 2)


IDLETIME.set_function(get_idletime)


def start_server(
    addr: str,
    port: int,
    registry: prometheus_client.registry.CollectorRegistry,
) -> None:
    """Start a WSGI server for Prometheus metrics."""
    app = prometheus_client.make_wsgi_app(registry)
    httpd = simple_server.make_server(addr, port, app)
    httpd.serve_forever()


if __name__ == "__main__":
    start_server(
        addr="", port=METRICS_PORT, registry=prometheus_client.REGISTRY
    )
