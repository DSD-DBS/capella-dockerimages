# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import json
import logging
import os
import pathlib
import re
import time

import docker.models.containers
import pytest

log = logging.getLogger(__file__)
log.setLevel("DEBUG")
client = docker.from_env()
from collections.abc import Generator

timeout = 120  # Timeout in seconds
default_env = {
    "T4C_LICENCE_SECRET": "",
    "RMT_PASSWORD": "my_long_password",
    "FILESERVICE_PASSWORD": "password",
    "T4C_USERNAME": "techuser",
}


@pytest.fixture(name="mode", params=["json", "repositories"])
def fixture_mode(request) -> str:
    return request.param


@pytest.fixture(
    name="container_success",
)
def fixture_container_success(
    mode: str,
    tmp_path: pathlib.Path,
) -> Generator[docker.models.containers.Container]:
    env = {
        "json": {
            **default_env,
            "T4C_JSON": json.dumps(
                [
                    {
                        "repository": "name",
                        "port": 2036,
                        "host": "instance-host",
                        "instance": "dev-5.0",
                    },
                    {
                        "repository": "name",
                        "port": 2036,
                        "host": "instance-host",
                        "instance": "dev-5.2",
                    },
                    {"repository": "test", "port": 2036, "host": "instance-host"},
                ]
            ),
        },
        "repositories": {
            **default_env,
            "T4C_SERVER_HOST": "instance-host",
            "T4C_SERVER_PORT": "2036",
            "T4C_REPOSITORIES": "repo1,repo2",
        },
    }[mode]
    yield get_container(environment=env, tmp_path=tmp_path)


@pytest.fixture(name="container_failure")
def fixture_container_failure(
    mode: str,
) -> Generator[docker.models.containers.Container]:
    env = {
        "json": {
            **default_env,
            "T4C_JSON": json.dumps(
                [
                    {
                        "repository": "duplicate-name",
                        "port": 2036,
                        "host": "instance-host",
                    },
                    {
                        "repository": "duplicate-name",
                        "port": 2036,
                        "host": "instance-host",
                    },
                    {"repository": "test", "port": 2036, "host": "instance-host"},
                ]
            ),
        },
        "repositories": {
            **default_env,
            "T4C_SERVER_HOST": "instance-host",
            "T4C_SERVER_PORT": "2036",
        },
    }[mode]
    yield get_container(environment=env)


def get_container(
    environment: dict[str, str], tmp_path: pathlib.Path = None
) -> Generator[docker.models.containers.Container]:
    log.info(tmp_path)
    volumes = (
        {
            str(tmp_path): {
                "bind": "/opt/capella/configuration",
                "model": "rw",
            }
        }
        if tmp_path
        else {}
    )
    container = None
    try:
        container = client.containers.run(
            image=os.getenv("DOCKER_CAPELLA_T4C_REMOTE", "t4c/client/remote"),
            detach=True,
            environment=environment | {"RMT_PASSWORD": "password"},
            volumes=volumes,
        )
        yield container
    finally:
        if container:
            container.stop()
            container.remove()


def wait_for_container(container: docker.models.containers.Container) -> None:
    log_line = 0
    for _ in range(int(timeout / 2)):
        log.info("Wait until INFO success: xrdp-sesman entered RUNNING state")

        splitted_logs = container.logs().decode().splitlines()
        log.debug("Current log: %s", "\n".join(splitted_logs[log_line:]))
        log_line = len(splitted_logs)

        if b"INFO success: xrdp-sesman entered RUNNING state" in container.logs():
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


@pytest.mark.t4c
def test_repositories_seeding(
    container_success: Generator[docker.models.containers.Container],
    mode: str,
    tmp_path: pathlib.Path,
):
    tmp_path.chmod(0o777)

    container = next(container_success)
    wait_for_container(container)

    path = tmp_path / "fr.obeo.dsl.viewpoint.collab" / "repository.properties"
    assert path.exists()
    file_content = path.read_text()

    if mode == "json":
        repositories = {
            r"name\\ \(dev-5.0\)": r"tcp\://instance-host\:2036/name",
            r"name\\ \(dev-5.2\)": r"tcp\://instance-host\:2036/name",
            r"test": r"tcp\://instance-host\:2036/test",
        }
    elif mode == "repositories":
        repositories = {
            r"repo1": r"tcp\://instance-host\:2036/repo1",
            r"repo2": r"tcp\://instance-host\:2036/repo2",
        }
    else:
        repositories = {}
    for key in repositories:
        assert repositories[key] == re.search(f"{key}=(.+)", file_content).group(1)


@pytest.mark.t4c
def test_invalid_env_variable(
    container_failure: Generator[docker.models.containers.Container],
):
    container = next(container_failure)
    with pytest.raises(RuntimeError):
        wait_for_container(container)
