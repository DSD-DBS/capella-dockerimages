# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import collections.abc as cabc
import contextlib
import logging
import os
import pathlib
import re
import shutil
import time

import docker
import pytest
import requests
from docker.models import containers
from requests import auth

log = logging.getLogger(__file__)
log.setLevel("DEBUG")
client = docker.from_env()

timeout = 120  # Timeout in seconds


HTTP_LOGIN: str = "admin"
HTTP_PASSWORD: str = "password"


T4C_REPO_HOST: str = "host.docker.internal"
T4C_REPO_NAME: str = "test-repo"
T4C_PROJECT_NAME: str = "test-project"
T4C_USERNAME: str = "admin"
T4C_PASSWORD: str = "password"

GIT_REPO_BRANCH: str = "backup-test"
GIT_EMAIL: str = "exporter@example.com"
GIT_USERNAME: str = "any"
GIT_PASSWORD: str = "any"


@contextlib.contextmanager
def get_container(
    image: str,
    ports: dict[str, int | None] | None = None,
    environment: dict[str, str] | None = None,
    path: pathlib.Path | None = None,
    mount_path: str | None = None,
    entrypoint: list[str] | None = None,
    use_docker_prefix: bool = True,
) -> cabc.Iterator[containers.Container]:
    volumes = (
        {
            str(path): {
                "bind": mount_path,
                "model": "rw",
            }
        }
        if path
        else {}
    )

    if use_docker_prefix:
        docker_prefix = os.getenv("DOCKER_PREFIX", "")
        docker_tag = os.getenv("DOCKER_TAG", "latest")
        image = f"{docker_prefix}{image}:{docker_tag}"

    container = client.containers.run(
        image=image,
        detach=True,
        ports=ports,
        environment=environment,
        volumes=volumes,
        extra_hosts={
            "host.docker.internal": "host-gateway",
        },
        entrypoint=entrypoint,
    )

    try:
        yield container
    finally:
        if container:
            container.stop()
            container.remove()


def wait_for_container(
    container: containers.Container, wait_for_message: str
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


def is_capella_5_x_x() -> bool:
    return bool(re.match(r"5.[0-9]+.[0-9]+", os.getenv("CAPELLA_VERSION", "")))


def is_capella_6_x_x() -> bool:
    return bool(re.match(r"6.[0-9]+.[0-9]+", os.getenv("CAPELLA_VERSION", "")))


def get_projects_of_t4c_repository(t4c_http_port: str) -> list[dict[str, str]]:
    assert t4c_http_port.isnumeric()

    res = requests.get(
        f"http://localhost:{t4c_http_port}/api/v1.0/projects/{T4C_REPO_NAME}",
        auth=_get_basic_auth(),
        timeout=60,
    )
    res.raise_for_status()
    return res.json()["projects"]


# In case you encounter a connection error here for the tests, first try:
# 1. deamon-reload
# 2. docker restart
# Related to: https://github.com/moby/moby/issues/42442
def create_t4c_repository(t4c_http_port: str):
    res = requests.post(
        f"http://localhost:{t4c_http_port}/api/v1.0/repositories",
        auth=_get_basic_auth(),
        timeout=60,
        json={
            "repositoryName": T4C_REPO_NAME,
            "authenticationType": "",
            "datasourceType": "H2_EMBEDDED",
        },
    )
    res.raise_for_status()

    assert res.status_code == 201


def _get_basic_auth() -> auth.HTTPBasicAuth:
    return auth.HTTPBasicAuth(HTTP_LOGIN, HTTP_PASSWORD)


@pytest.fixture(name="local_git_container")
def fixture_local_git_container() -> containers.Container:
    ports: dict[str, int | None] = {"80/tcp": None}

    with get_container(image="local-git-server", ports=ports) as container:
        wait_for_container(container, "server started")
        yield container


@pytest.fixture(name="git_port")
def fixture_git_port(local_git_container: containers.Containe) -> str:
    local_git_container.reload()
    return local_git_container.ports["80/tcp"][0]["HostPort"]


@pytest.fixture(name="git_general_environment")
def fixture_git_general_environment(git_port: str) -> dict[str, str]:
    return {
        "FILE_HANDLER": "GIT",
        "GIT_REPO_URL": f"http://host.docker.internal:{git_port}/git/git-test-repo.git",
        "GIT_REPO_BRANCH": GIT_REPO_BRANCH,
        "GIT_USERNAME": GIT_USERNAME,
        "GIT_PASSWORD": GIT_PASSWORD,
    }


@pytest.fixture(name="t4c_server_container")
def fixture_t4c_server_container() -> containers.Container:
    env: dict[str, str] = {"REST_API_PASSWORD": "password"}

    ports: dict[str, int | None] = {
        "2036/tcp": None,
        "8080/tcp": None,
        "12036/tcp": None,
    }

    with get_container(
        image="t4c/server/server", ports=ports, environment=env
    ) as container:
        wait_for_container(container, "!MESSAGE CDO server started")
        container.reload()
        create_t4c_repository(container.ports["8080/tcp"][0]["HostPort"])
        yield container


@pytest.fixture(name="t4c_server_ports")
def fixture_t4c_server_ports(
    t4c_server_container: containers.Container,
) -> tuple[str, str, str]:
    t4c_server_container.reload()
    return (
        t4c_server_container.ports["2036/tcp"][0]["HostPort"],
        t4c_server_container.ports["8080/tcp"][0]["HostPort"],
        t4c_server_container.ports["12036/tcp"][0]["HostPort"],
    )


@pytest.fixture(name="t4c_general_environment")
def fixture_t4c_general_environment(
    t4c_server_ports: tuple[str, str, str]
) -> dict[str, str]:
    return {
        "T4C_REPO_HOST": T4C_REPO_HOST,
        "T4C_REPO_PORT": t4c_server_ports[0],
        "T4C_CDO_PORT": t4c_server_ports[2],
        "T4C_REPO_NAME": T4C_REPO_NAME,
        "T4C_PROJECT_NAME": T4C_PROJECT_NAME,
        "T4C_USERNAME": T4C_USERNAME,
        "T4C_PASSWORD": T4C_PASSWORD,
        "INCLUDE_COMMIT_HISTORY": "false",
        "LOG_LEVEL": "INFO",
    }


@pytest.fixture(name="t4c_exporter_general_environment")
def fixture_t4c_exporter_general_environment(
    t4c_server_ports: tuple[str, str, str],
    t4c_general_environment: dict[str, str],
) -> dict[str, str]:
    return t4c_general_environment | {
        "HTTP_LOGIN": HTTP_LOGIN,
        "HTTP_PASSWORD": HTTP_PASSWORD,
        "HTTP_PORT": t4c_server_ports[1],
    }
