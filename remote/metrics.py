#!/usr/bin/env python

import os
import subprocess

from prometheus_client import Gauge, start_http_server

METRICS_PORT = int(
    os.getenv("METRICS_PORT", 9100)  # pylint: disable=invalid-envvar-default
)

IDLETIME = Gauge("idletime_seconds", "Idletime of X server in seconds from xprintidle")


def get_idletime() -> float:
    """Return output of xprintidle (Idle time of X server in millisecs)"""
    proc = subprocess.run(
        ["xprintidle"], check=True, capture_output=True, encoding="utf-8"
    )
    return round(int(proc.stdout) / 1000, 2)


IDLETIME.set_function(get_idletime)

if __name__ == "__main__":
    start_http_server(METRICS_PORT)
    while True:
        ...  # Prometheus metric server dies if there is no run_forever mechanism
