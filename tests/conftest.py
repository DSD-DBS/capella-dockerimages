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


@pytest.fixture(name="git_container")
def fixture_git_container() -> containers.Container:
    with get_container(image="local-git-server") as container:
        wait_for_container(container, "server started")
        yield container


@pytest.fixture(name="git_ip_addr")
def fixture_git_ip_addr(git_container: containers.Containe) -> str:
    git_container.reload()
    return git_container.attrs["NetworkSettings"]["IPAddress"]


@pytest.fixture(name="git_general_env")
def fixture_git_general_env(git_ip_addr: str) -> dict[str, str]:
    return {
        "FILE_HANDLER": "GIT",
        "GIT_REPO_URL": f"http://{git_ip_addr}:80/git/git-test-repo.git",
        "GIT_REPO_BRANCH": GIT_REPO_BRANCH,
        "GIT_USERNAME": GIT_USERNAME,
        "GIT_PASSWORD": GIT_PASSWORD,
    }


@pytest.fixture(name="t4c_server_volumes")
def fixture_t4c_server_volumes(
    tmp_path: pathlib.Path,
    request: pytest.FixtureRequest,
) -> dict[str, dict[str, str]] | None:
    if hasattr(request, "param") and request.param.get("init", False):
        server_test_data_path: pathlib.Path = tmp_path / "test-server-data"

        shutil.copytree(
            src=pathlib.Path(__file__).parents[0]
            / "t4c-server-test-data"
            / "data"
            / os.getenv("CAPELLA_VERSION", ""),
            dst=server_test_data_path,
        )

        return create_volume(server_test_data_path, "/data")

    return None


@pytest.fixture(name="t4c_server_env")
def fixture_t4c_server_env(request: pytest.FixtureRequest) -> dict[str, str]:
    env: dict[str, str] = {"REST_API_PASSWORD": "password"}

    if hasattr(request, "param"):
        env = env | request.param

    return env


@pytest.fixture(name="t4c_server_container")
def fixture_t4c_server_container(
    t4c_server_env: dict[str, str],
    t4c_server_volumes: dict[str, dict[str, str]] | None,
) -> containers.Container:
    wait_for_message: str = (
        "!MESSAGE Warmup done for repository"
        if t4c_server_volumes
        else "!MESSAGE CDO server started"
    )

    with get_container(
        image="t4c/server/server",
        environment=t4c_server_env,
        volumes=t4c_server_volumes,
    ) as container:
        wait_for_container(container, wait_for_message)
        yield container


@pytest.fixture(name="t4c_ip_addr")
def fixture_t4c_ip_addr(
    t4c_server_container: containers.Container,
) -> str:
    t4c_server_container.reload()
    return t4c_server_container.attrs["NetworkSettings"]["IPAddress"]


@pytest.fixture(name="t4c_general_env")
def fixture_t4c_general_env(t4c_ip_addr: str) -> dict[str, str]:
    return {
        "T4C_REPO_HOST": t4c_ip_addr,
        "T4C_REPO_PORT": "2036",
        "T4C_CDO_PORT": "12036",
        "T4C_REPO_NAME": T4C_REPO_NAME,
        "T4C_PROJECT_NAME": T4C_PROJECT_NAME,
        "T4C_USERNAME": T4C_USERNAME,
        "T4C_PASSWORD": T4C_PASSWORD,
        "INCLUDE_COMMIT_HISTORY": "false",
        "LOG_LEVEL": "INFO",
    }


@pytest.fixture(name="t4c_exporter_env")
def fixture_t4c_exporter_env(
    t4c_general_env: dict[str, str]
) -> dict[str, str]:
    return t4c_general_env | {
        "HTTP_LOGIN": HTTP_LOGIN,
        "HTTP_PASSWORD": HTTP_PASSWORD,
        "HTTP_PORT": "8080",
    }


@pytest.fixture(name="init_t4c_server_repo")
def fixture_init_t4c_server_repo(t4c_ip_addr: str):
    create_t4c_repository(t4c_ip_addr)
    yield


@contextlib.contextmanager
def get_container(
    image: str,
    ports: dict[str, int | None] | None = None,
    environment: dict[str, str] | None = None,
    volumes: dict[str, dict[str, str]] | None = None,
    entrypoint: list[str] | None = None,
    use_docker_prefix: bool = True,
) -> cabc.Iterator[containers.Container]:
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
        entrypoint=entrypoint,
    )

    try:
        yield container
    finally:
        if container:
            container.stop()
            container.remove()


def wait_for_container(container: containers.Container, wait_for_message: str):
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


def get_projects_of_t4c_repository(t4c_ip_addr: str) -> list[dict[str, str]]:
    res = requests.get(
        f"http://{t4c_ip_addr}:8080/api/v1.0/projects/{T4C_REPO_NAME}",
        auth=_get_basic_auth(),
        timeout=60,
    )
    res.raise_for_status()
    return res.json()["projects"]


# In case you encounter a connection error here for the tests, first try:
# 1. deamon-reload
# 2. docker restart
# Related to: https://github.com/moby/moby/issues/42442
def create_t4c_repository(t4c_ip_addr: str):
    res = requests.post(
        f"http://{t4c_ip_addr}:8080/api/v1.0/repositories",
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


def create_volume(
    path: str | pathlib.Path, mount_path: str | pathlib.Path
) -> dict[str, dict[str, str]]:
    return {
        str(path): {
            "bind": str(mount_path),
            "model": "rw",
        }
    }


def _get_basic_auth() -> auth.HTTPBasicAuth:
    return auth.HTTPBasicAuth(HTTP_LOGIN, HTTP_PASSWORD)
