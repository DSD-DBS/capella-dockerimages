# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import logging
import os
import pathlib
import re
import subprocess

import conftest
import pytest
from docker.models import containers

log = logging.getLogger(__file__)
log.setLevel("DEBUG")

CAPELLA_VERSION = os.getenv("CAPELLA_VERSION", "")


def is_capella_5_x_x() -> bool:
    return bool(re.match(r"5.[0-9]+.[0-9]+", CAPELLA_VERSION))


def is_capella_6_x_x() -> bool:
    return bool(re.match(r"6.[0-9]+.[0-9]+", CAPELLA_VERSION))


@pytest.fixture(name="local_git_container")
def fixture_local_git_container() -> containers.Container:
    ports: dict[str, int | None] = {"80/tcp": None}

    with conftest.get_container(
        image="local-git-server", ports=ports
    ) as container:
        conftest.wait_for_container(container, "server started")
        yield container


@pytest.fixture(name="t4c_backup_container")
def fixture_t4c_backup_container(
    local_git_container: containers.Container,
    t4c_server_container: containers.Container,
    request,
) -> containers.Container:
    t4c_server_container.reload()

    t4c_repo_port = t4c_server_container.ports["2036/tcp"][0]["HostPort"]
    t4c_cdo_port = t4c_server_container.ports["12036/tcp"][0]["HostPort"]

    if "HTTP_PORT" in request.param:
        request.param["HTTP_PORT"] = t4c_server_container.ports["8080/tcp"][0][
            "HostPort"
        ]

    local_git_container.reload()
    git_server_port = local_git_container.ports["80/tcp"][0]["HostPort"]

    env: dict[str, str] = {
        "GIT_REPO_URL": f"http://localhost:{git_server_port}/git/git-test-repo.git",
        "GIT_REPO_BRANCH": "backup-test",
        "GIT_USERNAME": "any",
        "GIT_PASSWORD": "any",
        "T4C_REPO_HOST": "127.0.0.1",
        "T4C_REPO_PORT": t4c_repo_port,
        "T4C_CDO_PORT": t4c_cdo_port,
        "T4C_REPO_NAME": "test-repo",
        "T4C_PROJECT_NAME": "test-project",
        "T4C_USERNAME": "admin",
        "T4C_PASSWORD": "password",
        "LOG_LEVEL": "INFO",
        "INCLUDE_COMMIT_HISTORY": "false",
    } | request.param

    with conftest.get_container(
        image="t4c/client/backup", environment=env, network="host"
    ) as container:
        yield container


@pytest.fixture(name="t4c_server_container")
def fixture_t4c_server_container(request) -> containers.Container:
    env: dict[str, str] = {"REST_API_PASSWORD": "password"} | request.param

    ports: dict[str, int | None] = {
        "2036/tcp": None,
        "8080/tcp": None,
        "12036/tcp": None,
    }

    with conftest.get_container(
        image="t4c/server/server",
        ports=ports,
        environment=env,
        path=pathlib.Path(__file__).parents[0]
        / "t4c-server-test-data"
        / "data"
        / CAPELLA_VERSION,
        mount_path="/data",
    ) as container:
        conftest.wait_for_container(
            container, "!MESSAGE Warmup done for repository test-repo."
        )
        yield container


@pytest.mark.t4c_server
@pytest.mark.parametrize(
    "t4c_server_container,t4c_backup_container",
    [
        pytest.param({"ENABLE_CDO": "true"}, {"CONNECTION_TYPE": "telnet"}),
        pytest.param(
            {"ENABLE_CDO": "false"},
            {"CONNECTION_TYPE": "telnet"},
            marks=pytest.mark.skipif(
                condition=is_capella_6_x_x(),
                reason="CDO disabled by default for capella >= 6.0.0",
            ),
        ),
        pytest.param(
            {"ENABLE_CDO": "false"},
            {
                "CONNECTION_TYPE": "http",
                "HTTP_LOGIN": "admin",
                "HTTP_PASSWORD": "password",
                "HTTP_PORT": None,
            },
            marks=pytest.mark.skipif(
                condition=is_capella_5_x_x(),
                reason="conncetion type http is not supported for capella < 6.0.0",
            ),
        ),
    ],
    indirect=True,
)
def test_model_backup_happy(
    t4c_backup_container: containers.Container,
    local_git_container: containers.Container,
    tmp_path: pathlib.Path,
):
    conftest.wait_for_container(t4c_backup_container, "Backup finished")

    git_server_port = local_git_container.ports["80/tcp"][0]["HostPort"]
    subprocess.run(
        [
            "git",
            "clone",
            f"http://localhost:{git_server_port}/git/git-test-repo.git",
            tmp_path,
        ],
        check=True,
    )
    try:
        subprocess.run(
            ["git", "switch", "backup-test"], check=True, cwd=tmp_path
        )
    except subprocess.CalledProcessError:
        log.debug("backup failed - backup-test branch does not exists")
        raise

    assert os.path.exists(tmp_path / ".project")
    assert os.path.exists(tmp_path / "test-project.afm")
    assert os.path.exists(tmp_path / "test-project.aird")
    assert os.path.exists(tmp_path / "test-project.capella")


@pytest.mark.t4c_server
@pytest.mark.parametrize(
    "t4c_server_container,t4c_backup_container",
    [
        # CONNECTION_TYPE "unknown" is not allowed
        ({"ENABLE_CDO": "true"}, {"CONNECTION_TYPE": "unknown"}),
        pytest.param(
            {"ENABLE_CDO": "false"},
            {"CONNECTION_TYPE": "telnet"},
            marks=pytest.mark.skipif(
                condition=is_capella_5_x_x(),
                reason="CDO enabled by default for capella < 6.0.0",
            ),
        ),
        ({"ENABLE_CDO": "false"}, {"CONNECTION_TYPE": "http"}),
    ],
    indirect=True,
)
def test_model_backup_unhappy(t4c_backup_container):
    with pytest.raises(RuntimeError):
        conftest.wait_for_container(t4c_backup_container, "Backup finished")
