# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import logging
import os
import pathlib
import time
from collections.abc import Iterator

import docker
import docker.models.containers

log = logging.getLogger(__file__)
log.setLevel("DEBUG")
client = docker.from_env()

timeout = 120  # Timeout in seconds


def get_container(
    image: str,
    environment: dict[str, str],
    tmp_path: pathlib.Path | None = None,
    mount_path: str | None = None,
) -> Iterator[docker.models.containers.Container]:
    volumes = (
        {
            str(tmp_path): {
                "bind": mount_path,
                "model": "rw",
            }
        }
        if tmp_path
        else {}
    )
    container = None
    docker_prefix = os.getenv("DOCKER_PREFIX", "")
    docker_tag = os.getenv("DOCKER_TAG", "latest")

    try:
        container = client.containers.run(
            image=f"{docker_prefix}{image}:{docker_tag}",
            detach=True,
            environment=environment | {"RMT_PASSWORD": "password"},
            volumes=volumes,
        )
        yield container
    finally:
        if container:
            container.stop()
            container.remove()


def wait_for_container(
    container: docker.models.containers.Container, wait_for_message: str
) -> None:
    log_line = 0
    for _ in range(int(timeout / 2)):
        log.info("Wait until %s", wait_for_message)

        splitted_logs = container.logs().decode().splitlines()
        log.debug("Current log: %s", "\n".join(splitted_logs[log_line:]))
        log_line = len(splitted_logs)

        if wait_for_message in container.logs().decode():
            log.info("Found log line %s", wait_for_message)
            break
        container.reload()
        if container.status == "exited":
            log.error("Log from container: %s", container.logs().decode())
            raise RuntimeError("Container exited unexpectedly")

        time.sleep(2)

    else:
        log.error("Log from container: %s", container.logs().decode())
        raise TimeoutError("Timeout while waiting for model loading")
