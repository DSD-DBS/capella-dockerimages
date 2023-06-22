# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import collections.abc as cabc
import contextlib
import logging
import multiprocessing
import os
import pathlib
import queue
import re
import shutil
import subprocess
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


DOCKER_NETWORK: str = os.getenv("DOCKER_NETWORK", "host")
CAPELLA_VERSION: str = os.getenv("CAPELLA_VERSION", "")
ENTRYPOINT: str = f"/{CAPELLA_VERSION}/test-project.aird"


@pytest.fixture(name="git_container")
def fixture_git_container() -> containers.Container:
    with get_container(
        image="local-git-server",
        image_prefix="",
        image_tag=os.getenv("LOCAL_GIT_TAG", None),
        ports={"80/tcp": None} if DOCKER_NETWORK == "host" else None,
    ) as container:
        wait_for_container(container, "server started")
        yield container


@pytest.fixture(name="git_ip_addr")
def fixture_git_ip_addr(git_container: containers.Container) -> str:
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


@pytest.fixture(name="init_git_server")
def fixture_init_git_server(
    git_ip_addr: str,
    git_http_port: str,
    tmp_path: pathlib.Path,
):
    clone_git_repository(git_ip_addr, git_http_port, tmp_path)
    copy_test_project_into_git_repo(tmp_path)
    commit_and_push_git_repo(tmp_path)
    yield


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
            destination_path=server_test_data_tar_path,
            source_dir=(
                pathlib.Path(__file__).parents[0]
                / "t4c-server-test-data"
                / "data"
                / CAPELLA_VERSION
            ),
            arcname="data",
        )
        wait_for_message = "!MESSAGE Warmup done for repository"

    if image_prefix := os.getenv("T4C_SERVER_REGISTRY", None):
        image_prefix += "/"

    with get_container(
        image="t4c/server/server",
        image_prefix=image_prefix,
        image_tag=os.getenv("T4C_SERVER_TAG", None),
        environment=t4c_server_env,
        ports={"8080/tcp": None} if DOCKER_NETWORK == "host" else None,
        entrypoint=["/bin/bash"],
    ) as container:
        if init:
            # We can't just mount the test data as a volume as this will cause problems
            # when as we are running Docker in Docker (i.e., we would mount the
            # volume on the host machine but not on the container running the job/test)
            with open(file=server_test_data_tar_path, mode="rb") as tar_file:
                client.api.put_archive(container.id, "/", tar_file)
        wait_for_container(container, wait_for_message, cmd="/opt/startup.sh")
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
    if DOCKER_NETWORK == "host":
        return t4c_server_container.ports["8080/tcp"][0]["HostPort"]
    return "8080"


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
    image_prefix: str | None = None,
    image_tag: str | None = None,
    ports: dict[str, int | None] | None = None,
    environment: dict[str, str] | None = None,
    volumes: dict[str, dict[str, str]] | None = None,
    entrypoint: list[str] | None = None,
    command: str | list[str] | None = None,
) -> cabc.Iterator[containers.Container]:
    docker_prefix = (
        image_prefix
        if image_prefix is not None
        else os.getenv("DOCKER_PREFIX", "")
    )

    docker_tag = (
        image_tag
        if image_tag is not None
        else os.getenv("DOCKER_TAG", "latest")
    )

    image = f"{docker_prefix}{image}:{docker_tag}"

    container = client.containers.run(
        image=image,
        command=command,
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
    cmd: str | None = None,
):
    start_time = time.time()

    log_queue: multiprocessing.Queue = multiprocessing.Queue()

    fetch_log_process = multiprocessing.Process(
        target=fetch_logs, args=(container.id, log_queue, cmd)
    )

    container.reload()
    if container.status == "exited":
        log.error("Log from container:\n%s", container.logs().decode())
        raise RuntimeError("Container exited unexpectedly")

    fetch_log_process.start()

    log.info("Wait until log line: %s", wait_for_message)
    decoded_log = ""
    while time.time() - start_time < timeout:
        try:
            decoded_log += log_queue.get(timeout=4)

            if wait_for_message in decoded_log:
                log.info(
                    "Found log line %s in %d seconds",
                    wait_for_message,
                    time.time() - start_time,
                )
                log.debug("Whole log:\n%s", decoded_log)
                fetch_log_process.terminate()
                return

        except queue.Empty:
            if log_queue.empty():
                container.reload()
                if container.status == "exited":
                    log.error("Log from container:\n%s", decoded_log)
                    fetch_log_process.terminate()
                    raise RuntimeError("Container exited unexpectedly")

    if time.time() - start_time > timeout:
        log.error("Log from container:\n%s", decoded_log)
        fetch_log_process.terminate()
        raise TimeoutError(
            f"Timeout while waiting for container '{container.name}' with image '{container.image}'"
        )


def fetch_logs(container_id: int, log_queue, cmd: str | None = None):
    container = client.containers.get(container_id=container_id)

    if cmd:
        _, stream = container.exec_run(cmd=cmd, stream=True)
    else:
        stream = container.logs(stream=True)

    assert stream

    cur_line = ""
    for chunk in stream:
        encoding = chardet.detect(chunk)["encoding"]

        if encoding:
            chunk_decoded = chunk.decode(encoding)
            cur_line += chunk_decoded

            if "\n" in chunk_decoded:
                log_queue.put(cur_line)
                cur_line = ""
        else:
            log.error("Encoding for %s is unknown", chunk)
    log_queue.put(cur_line)


def is_capella_5_x_x() -> bool:
    return bool(re.match(r"5.[0-9]+.[0-9]+", CAPELLA_VERSION))


def is_capella_6_x_x() -> bool:
    return bool(re.match(r"6.[0-9]+.[0-9]+", CAPELLA_VERSION))


def get_projects_of_t4c_repository(
    t4c_ip_addr: str, t4c_http_port: str
) -> list[dict[str, str]]:
    if DOCKER_NETWORK == "host":
        t4c_ip_addr = "127.0.0.1"

    os.environ["no_proxy"] = os.getenv("no_proxy", "") + f",{t4c_ip_addr}"

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

    os.environ["no_proxy"] = os.getenv("no_proxy", "") + f",{t4c_ip_addr}"

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
    destination_path: str | pathlib.Path,
    source_dir: str | pathlib.Path,
    arcname: str,
):
    with tarfile.open(name=destination_path, mode="w") as tar_file:
        tar_file.add(name=source_dir, arcname=arcname)


def extract_container_dir_to_local_dir(
    container_id: str, container_dir: str, target_dir: pathlib.Path
):
    target_dir.mkdir(parents=True, exist_ok=True)
    tar_file_name = target_dir / (container_dir.split("/")[-1] + ".tar")

    stream, _ = client.api.get_archive(container_id, container_dir)

    with open(file=tar_file_name, mode="wb") as tar_file:
        for chunk in stream:
            tar_file.write(chunk)

    with tarfile.open(name=tar_file_name, mode="r") as tar_file:
        tar_file.extractall(path=target_dir)


def clone_git_repository(
    git_ip_addr: str, git_http_port: str, path: pathlib.Path
):
    if DOCKER_NETWORK == "host":
        git_ip_addr = "127.0.0.1"

    env = os.environ
    env["no_proxy"] = f"{os.getenv('no_proxy', '')},{git_ip_addr}"

    subprocess.run(  # pylint: disable=subprocess-run-check
        [
            "git",
            "clone",
            f"http://{git_ip_addr}:{git_http_port}/git/git-test-repo.git",
            path,
        ],
        env=env,
        check=True,
        text=True,
        capture_output=True,
    )
    subprocess.run(  # pylint: disable=subprocess-run-check
        ["git", "switch", "-c", GIT_REPO_BRANCH],
        cwd=path,
        check=True,
        text=True,
        capture_output=True,
    )


def copy_test_project_into_git_repo(git_path: pathlib.Path):
    target_dir: pathlib.Path = pathlib.Path(
        git_path,
        str(pathlib.Path(ENTRYPOINT).parent).lstrip("/"),
    )
    target_dir.mkdir(exist_ok=True, parents=True)

    project_dir: pathlib.Path = (
        pathlib.Path(__file__).parents[0] / "data" / CAPELLA_VERSION
    )

    for file in project_dir.glob("*"):
        if not str(file).endswith("license"):
            shutil.copy2(file, target_dir)


def commit_and_push_git_repo(path: pathlib.Path):
    subprocess.run(  # pylint: disable=subprocess-run-check
        ["git", "config", "user.email", GIT_EMAIL],
        cwd=path,
        check=True,
        text=True,
        capture_output=True,
    )

    subprocess.run(  # pylint: disable=subprocess-run-check
        ["git", "config", "user.name", GIT_USERNAME],
        cwd=path,
        check=True,
        text=True,
        capture_output=True,
    )

    subprocess.run(  # pylint: disable=subprocess-run-check
        ["git", "add", "."],
        cwd=path,
        check=True,
        text=True,
        capture_output=True,
    )

    subprocess.run(  # pylint: disable=subprocess-run-check
        [
            "git",
            "-c",
            "commit.gpgsign=false",
            "commit",
            "--message",
            "test: Exporter test",
        ],
        cwd=path,
        check=True,
        text=True,
        capture_output=True,
    )

    subprocess.run(  # pylint: disable=subprocess-run-check
        ["git", "push", "origin", GIT_REPO_BRANCH],
        env={
            "GIT_USERNAME": GIT_USERNAME,
            "GIT_PASSWORD": GIT_PASSWORD,
            "GIT_ASKPASS": "/etc/git_askpass.py",
        },
        cwd=path,
        check=True,
        text=True,
        capture_output=True,
    )


def _get_basic_auth() -> auth.HTTPBasicAuth:
    return auth.HTTPBasicAuth(HTTP_LOGIN, HTTP_PASSWORD)
