# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import collections.abc as cabc
import contextlib
import logging
import os
import pathlib
import re
import tarfile
import time
import typing as t

import chardet
import docker
import pytest
import requests
from docker.models import containers
from requests import auth

log = logging.getLogger(__file__)
log.setLevel("DEBUG")
client = docker.from_env()

timeout = 60  # Timeout in seconds


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


DOCKER_NETWORK: str = os.getenv("DOCKER_NETWORK", "host")


@pytest.fixture(name="git_container")
def fixture_git_container() -> containers.Container:
    with get_container(
        image="local-git-server",
        image_tag_env="LOCAL_GIT_TAG",
        ports={"80/tcp": None} if DOCKER_NETWORK == "host" else None,
    ) as container:
        wait_for_container(container, "server started")
        yield container


@pytest.fixture(name="git_ip_addr")
def fixture_git_ip_addr(git_container: containers.Containe) -> str:
    git_container.reload()
    return git_container.attrs["NetworkSettings"]["IPAddress"]


@pytest.fixture(name="git_http_port")
def fixture_git_http_port(git_container: containers.Container) -> str:
    git_container.reload()
    if DOCKER_NETWORK == "host":
        return git_container.ports["80/tcp"][0]["HostPort"]
    return "80"


@pytest.fixture(name="git_general_env")
def fixture_git_general_env(git_ip_addr: str) -> dict[str, str]:
    return {
        "FILE_HANDLER": "GIT",
        "GIT_REPO_URL": f"http://{git_ip_addr}:80/git/git-test-repo.git",
        "GIT_REPO_BRANCH": GIT_REPO_BRANCH,
        "GIT_USERNAME": GIT_USERNAME,
        "GIT_PASSWORD": GIT_PASSWORD,
    }


@pytest.fixture(name="t4c_server_env")
def fixture_t4c_server_env(request: pytest.FixtureRequest) -> dict[str, str]:
    env: dict[str, str] = {"REST_API_PASSWORD": "password"}

    if hasattr(request, "param"):
        env = env | request.param

    return env


@pytest.fixture(name="t4c_server_container")
def fixture_t4c_server_container(
    t4c_server_env: dict[str, str],
    tmp_path: pathlib.Path,
    request: pytest.FixtureRequest,
) -> containers.Container:
    init = hasattr(request, "param") and request.param.get("init", False)
    server_test_data_tar_path = tmp_path / "test-server-data.tar"

    wait_for_message = "!MESSAGE CDO server started"
    if init:
        create_tarfile(
            tar_file_path=server_test_data_tar_path,
            source_dir=(
                pathlib.Path(__file__).parents[0]
                / "t4c-server-test-data"
                / "data"
                / os.getenv("CAPELLA_VERSION", "")
            ),
            arcname="data",
        )
        wait_for_message = "!MESSAGE Warmup done for repository"

    with get_container(
        image="t4c/server/server",
        image_tag_env="T4C_SERVER_TAG",
        environment=t4c_server_env,
        ports={"8080/tcp": None},
        entrypoint=["/bin/bash"],
    ) as container:
        if init:
            # We can't just mount the test data as a volume as this will cause problems
            # in our pipeline as we are running Docker in Docker (i.e., we would mount the
            # volume on the host machine but not on the container running the job/test)
            with open(file=server_test_data_tar_path, mode="rb") as tar_file:
                client.api.put_archive(container.id, "/", tar_file)
        _, stream = container.exec_run(cmd="/opt/startup.sh", stream=True)
        wait_for_container(container, wait_for_message, stream=stream)
        yield container


@pytest.fixture(name="t4c_ip_addr")
def fixture_t4c_ip_addr(
    t4c_server_container: containers.Container,
) -> str:
    t4c_server_container.reload()
    return t4c_server_container.attrs["NetworkSettings"]["IPAddress"]


@pytest.fixture(name="t4c_http_port")
def fixture_t4c_http_port(t4c_server_container: containers.Container) -> str:
    t4c_server_container.reload()
    return t4c_server_container.ports["8080/tcp"][0]["HostPort"]


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
def fixture_init_t4c_server_repo(t4c_ip_addr: str, t4c_http_port: str):
    create_t4c_repository(t4c_ip_addr, t4c_http_port)
    yield


@contextlib.contextmanager
def get_container(
    image: str,
    image_tag_env: str | None = None,
    ports: dict[str, int | None] | None = None,
    environment: dict[str, str] | None = None,
    volumes: dict[str, dict[str, str]] | None = None,
    entrypoint: list[str] | None = None,
) -> cabc.Iterator[containers.Container]:
    docker_prefix = os.getenv("DOCKER_PREFIX", "")
    if image_tag_env and (
        image_tag_env_value := os.getenv(image_tag_env, None)
    ):
        docker_tag = image_tag_env_value
    else:
        docker_tag = os.getenv("DOCKER_TAG", "latest")

    image = f"{docker_prefix}{image}:{docker_tag}"

    container = client.containers.run(
        image=image,
        ports=ports,
        environment=environment,
        volumes=volumes,
        entrypoint=entrypoint,
        network=DOCKER_NETWORK if DOCKER_NETWORK != "host" else None,
        labels={"capella-dockerimages-pytest-container": "true"},
        detach=True,
        tty=True,
    )

    try:
        yield container
    finally:
        if container:
            container.stop()
            container.remove()


def wait_for_container(
    container: containers.Container,
    wait_for_message: str,
    stream: t.BinaryIO | None = None,
):
    start_time = time.time()

    if not stream:
        stream = container.logs(stream=True)
    assert stream

    decoded_output: str = ""
    log.info("Wait until log line: %s", wait_for_message)
    for data in stream:
        encoding = chardet.detect(data)["encoding"]

        if encoding:
            _data = data.decode(encoding)
            decoded_output = decoded_output + _data

            if "\n" in _data:
                if wait_for_message in decoded_output:
                    log.info(
                        "Found log line %s in %d seconds",
                        wait_for_message,
                        time.time() - start_time,
                    )
                    log.debug("Whole log:\n%s", decoded_output)
                    return

        if time.time() - start_time > timeout:
            log.error("Log from container:\n%s", decoded_output)
            raise TimeoutError("Timeout while waiting for model loading")

    container.reload()
    if container.status == "exited":
        log.error("Log from container:\n%s", decoded_output)
        raise RuntimeError("Container exited unexpectedly")


def is_capella_5_x_x() -> bool:
    return bool(re.match(r"5.[0-9]+.[0-9]+", os.getenv("CAPELLA_VERSION", "")))


def is_capella_6_x_x() -> bool:
    return bool(re.match(r"6.[0-9]+.[0-9]+", os.getenv("CAPELLA_VERSION", "")))


def get_projects_of_t4c_repository(
    t4c_ip_addr: str, t4c_http_port: str
) -> list[dict[str, str]]:
    if DOCKER_NETWORK == "host":
        t4c_ip_addr = "127.0.0.1"

    res = requests.get(
        f"http://{t4c_ip_addr}:{t4c_http_port}/api/v1.0/projects/{T4C_REPO_NAME}",
        auth=_get_basic_auth(),
        timeout=60,
    )
    res.raise_for_status()
    return res.json()["projects"]


# In case you encounter a connection error here for the tests, first try:
# 1. deamon-reload
# 2. docker restart
# Related to: https://github.com/moby/moby/issues/42442
def create_t4c_repository(t4c_ip_addr: str, t4c_http_port: str):
    if DOCKER_NETWORK == "host":
        t4c_ip_addr = "127.0.0.1"

    res = requests.post(
        f"http://{t4c_ip_addr}:{t4c_http_port}/api/v1.0/repositories",
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


def create_tarfile(
    tar_file_path: str | pathlib.Path,
    source_dir: str | pathlib.Path,
    arcname: str,
):
    with tarfile.open(name=tar_file_path, mode="w") as tar_file:
        tar_file.add(name=source_dir, arcname=arcname)


def extract_container_dir_to_local_dir(
    container_id: str, container_dir: str, target_dir: pathlib.Path
):
    target_dir.mkdir(parents=True, exist_ok=True)
    tar_file_name = target_dir / (container_dir.split("/")[-1] + ".tar")

    strm, _ = client.api.get_archive(container_id, container_dir)

    with open(file=tar_file_name, mode="wb") as tar_file:
        for chunk in strm:
            tar_file.write(chunk)

    with tarfile.open(name=tar_file_name, mode="r") as tar_file:
        tar_file.extractall(path=target_dir)


def _get_basic_auth() -> auth.HTTPBasicAuth:
    return auth.HTTPBasicAuth(HTTP_LOGIN, HTTP_PASSWORD)
