# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import json
import logging
import os
import pathlib
import time

import docker
import docker.models.containers
import pytest

log = logging.getLogger(__file__)
log.setLevel("DEBUG")
client = docker.from_env()
from collections.abc import Generator

timeout = 120  # Timeout in seconds


@pytest.fixture(name="mode", params=["json", "legacy"])
def fixture_mode(request) -> str:
    return request.param


@pytest.fixture(
    name="container_success",
)
def fixture_container_success(
    mode: str, tmp_path: pathlib.Path
) -> Generator[docker.models.containers.Container]:
    env = {
        "json": {
            "GIT_REPOS_JSON": json.dumps(
                [
                    {
                        "url": "https://github.com/DSD-DBS/py-capellambse.git",
                        "revision": "master",
                        "depth": 1,
                        "entrypoint": "tests/data/melodymodel/5_2/Melody Model Test.aird",
                    },
                    {
                        "url": "https://github.com/DSD-DBS/collab-platform-arch.git",
                        "revision": "main",
                        "depth": 5,
                        "entrypoint": "collab-platform-arch.aird",
                    },
                ]
            ),
        },
        "legacy": {
            "GIT_URL": "https://github.com/DSD-DBS/collab-platform-arch.git",
            "GIT_ENTRYPOINT": "collab-platform-arch.aird",
            "GIT_REVISION": "main",
            "GIT_DEPTH": 0,
        },
    }[mode]
    yield get_container(environment=env, tmp_path=tmp_path)


@pytest.fixture(name="container_failure")
def fixture_container_failure(
    mode: str,
) -> Generator[docker.models.containers.Container]:
    env = {
        "json": {
            "GIT_REPOS_JSON": json.dumps(
                [
                    {
                        "url": "https://example.com/invalid-repository",
                        "revision": "main",
                        "depth": 0,
                        "entrypoint": "invalid.aird",
                    },
                ]
            ),
        },
        "legacy": {
            "GIT_URL": "https://example.com/invalid-repository",
            "GIT_ENTRYPOINT": "invalid.aird",
            "GIT_REVISION": "main",
            "GIT_DEPTH": 0,
        },
    }[mode]
    yield get_container(environment=env)


def get_container(
    environment: dict[str, str], tmp_path: pathlib.Path = None
) -> Generator[docker.models.containers.Container]:
    volumes = {}
    if tmp_path:
        volumes = {
            str(tmp_path): {
                "bind": "/workspace",
                "mode": "rw",
            }
        }

    try:
        container = client.containers.run(
            image=os.getenv("DOCKER_CAPELLA_READONLY", "capella/readonly"),
            detach=True,
            environment=environment | {"RMT_PASSWORD": "password"},
            volumes=volumes,
        )
        yield container
    finally:
        container.stop()
        container.remove()


def wait_for_container(container: docker.models.containers.Container) -> None:
    log_line = 0
    for _ in range(int(timeout / 2)):
        log.info("Wait until ---START_SESSION---")

        splitted_logs = container.logs().decode().splitlines()
        log.debug("Current log: %s", "\n".join(splitted_logs[log_line:]))
        log_line = len(splitted_logs)

        if b"---START_SESSION---" in container.logs():
            log.info("Loading of model finished")
            break
        container.reload()
        if container.status == "exited":
            log.error("Log from container: %s", container.logs().decode())
            raise RuntimeError("Container exited unexpectedly")

        time.sleep(2)

    else:
        log.error("Log from container: %s", container.logs().decode())
        raise TimeoutError("Timeout while waiting for model loading")


def test_model_loading(
    container_success: Generator[docker.models.containers.Container],
    mode: str,
    tmp_path: pathlib.Path,
):
    container = next(container_success)
    wait_for_container(container)

    number_of_files = len(list(tmp_path.iterdir()))
    if mode == "legacy":
        assert number_of_files == 2
    else:
        assert number_of_files == 3


def test_invalid_url_fails(
    container_failure: Generator[docker.models.containers.Container],
):
    container = next(container_failure)
    with pytest.raises(RuntimeError):
        wait_for_container(container)
