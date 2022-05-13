#!/usr/bin/env python

import os
import subprocess
from datetime import datetime, timedelta

from prometheus_client import Gauge, start_http_server

METRICS_PORT = int(
    os.getenv("METRICS_PORT", 9118)  # pylint: disable=invalid-envvar-default
)

IDLETIME = Gauge("idletime_seconds", "Idletime of X server in seconds from xprintidle")


class IdleTime:
    """Measure the idle time of the X server even if there is no X server."""

    def __init__(self) -> None:
        self.last_checkpoint = (datetime.now(), 0.0)

    def get_idletime(self) -> float:
        """
        Return idle time in seconds.

        If there us an X server return output of xprintidle
        (Idle time of X server in millisecs) in seconds. If there is no
        display the idle time increases. Then the timedelta from now and
        the last successfull xprintidle exec is returned.
        """
        proc = subprocess.run(
            ["xprintidle"], check=True, capture_output=True, encoding="utf-8"
        )
        if proc.stdout == "couldn't open display":
            checkpoint, idle_time = self.last_checkpoint
            delta = datetime.now() - checkpoint
            return (delta + timedelta(seconds=idle_time)).seconds

        current_idle_time = float(proc.stdout)
        self.last_checkpoint = (datetime.now(), current_idle_time)
        return round(current_idle_time / 1000, 2)


idler = IdleTime()

if __name__ == "__main__":
    IDLETIME.set_function(idler.get_idletime)
    start_http_server(METRICS_PORT)
    while True:
        ...  # Prometheus metric server dies if there is no run_forever mechanism
