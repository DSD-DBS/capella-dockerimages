# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import logging
import os
import pathlib
import shutil
import subprocess

import conftest
import pytest
from docker.models import containers

log = logging.getLogger(__file__)
log.setLevel("DEBUG")

pytestmark = pytest.mark.t4c_server


@pytest.fixture(name="t4c_server_container_parametrized")
def fixture_t4c_server_container_parametrized(
    tmp_path: pathlib.Path, request
) -> containers.Container:
    env: dict[str, str] = {"REST_API_PASSWORD": "password"} | request.param

    ports: dict[str, int | None] = {
        "2036/tcp": None,
        "8080/tcp": None,
        "12036/tcp": None,
    }

    server_test_data_path = tmp_path / "test-server-data"

    shutil.copytree(
        src=pathlib.Path(__file__).parents[0]
        / "t4c-server-test-data"
        / "data"
        / os.getenv("CAPELLA_VERSION", ""),
        dst=server_test_data_path,
    )

    with conftest.get_container(
        image="t4c/server/server",
        ports=ports,
        environment=env,
        path=server_test_data_path,
        mount_path="/data",
    ) as container:
        conftest.wait_for_container(
            container, "!MESSAGE Warmup done for repository test-repo."
        )
        yield container


@pytest.fixture(name="t4c_server_ports_parametrized")
def fixture_t4c_server_ports_parametrized(
    t4c_server_container_parametrized: containers.Container,
) -> tuple[str, str, str]:
    t4c_server_container_parametrized.reload()
    return (
        t4c_server_container_parametrized.ports["2036/tcp"][0]["HostPort"],
        t4c_server_container_parametrized.ports["8080/tcp"][0]["HostPort"],
        t4c_server_container_parametrized.ports["12036/tcp"][0]["HostPort"],
    )


@pytest.fixture(name="t4c_backups_prametrized_environment")
def fixture_t4c_backups_prametrized_environment(
    t4c_server_ports_parametrized: tuple[str, str, str],
) -> dict[str, str]:
    t4c_repo_port, _, t4c_cdo_port = t4c_server_ports_parametrized
    return {
        "T4C_REPO_HOST": conftest.T4C_REPO_HOST,
        "T4C_REPO_PORT": t4c_repo_port,
        "T4C_CDO_PORT": t4c_cdo_port,
        "T4C_REPO_NAME": conftest.T4C_REPO_NAME,
        "T4C_PROJECT_NAME": conftest.T4C_PROJECT_NAME,
        "T4C_USERNAME": conftest.T4C_USERNAME,
        "T4C_PASSWORD": conftest.T4C_PASSWORD,
        "INCLUDE_COMMIT_HISTORY": "false",
        "LOG_LEVEL": "INFO",
    }


@pytest.fixture(name="t4c_backup_container_parametrized")
def fixture_t4c_backup_container(
    git_general_environment: dict[str, str],
    t4c_backups_prametrized_environment: dict[str, str],
    t4c_server_ports_parametrized: tuple[str, str, str],
    request,
) -> containers.Container:
    if "HTTP_PORT" in request.param:
        request.param["HTTP_PORT"] = t4c_server_ports_parametrized[1]

    env: dict[str, str] = (
        git_general_environment
        | t4c_backups_prametrized_environment
        | request.param
    )

    with conftest.get_container(
        image="t4c/client/backup", environment=env, network="host"
    ) as container:
        yield container


@pytest.mark.parametrize(
    "t4c_server_container_parametrized,t4c_backup_container_parametrized",
    [
        pytest.param({"ENABLE_CDO": "true"}, {"CONNECTION_TYPE": "telnet"}),
        pytest.param(
            {"ENABLE_CDO": "false"},
            {"CONNECTION_TYPE": "telnet"},
            marks=pytest.mark.skipif(
                condition=conftest.is_capella_6_x_x(),
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
                condition=conftest.is_capella_5_x_x(),
                reason="conncetion type http is not supported for capella < 6.0.0",
            ),
        ),
    ],
    indirect=True,
)
def test_model_backup_happy(
    t4c_backup_container_parametrized: containers.Container,
    local_git_container: containers.Container,
    tmp_path: pathlib.Path,
):
    conftest.wait_for_container(
        t4c_backup_container_parametrized, "Backup finished"
    )

    git_path = tmp_path / "test-git-data"
    git_path.mkdir()

    git_server_port = local_git_container.ports["80/tcp"][0]["HostPort"]
    subprocess.run(
        [
            "git",
            "clone",
            f"http://localhost:{git_server_port}/git/git-test-repo.git",
            git_path,
        ],
        check=True,
    )
    try:
        subprocess.run(
            ["git", "switch", "backup-test"], check=True, cwd=git_path
        )
    except subprocess.CalledProcessError:
        log.debug("backup failed - backup-test branch does not exists")
        raise

    assert os.path.exists(git_path / ".project")
    assert os.path.exists(git_path / "test-project.afm")
    assert os.path.exists(git_path / "test-project.aird")
    assert os.path.exists(git_path / "test-project.capella")


@pytest.mark.parametrize(
    "t4c_server_container_parametrized,t4c_backup_container_parametrized",
    [
        # CONNECTION_TYPE "unknown" is not allowed
        ({"ENABLE_CDO": "true"}, {"CONNECTION_TYPE": "unknown"}),
        pytest.param(
            {"ENABLE_CDO": "false"},
            {"CONNECTION_TYPE": "telnet"},
            marks=pytest.mark.skipif(
                condition=conftest.is_capella_5_x_x(),
                reason="CDO enabled by default for capella < 6.0.0",
            ),
        ),
        ({"ENABLE_CDO": "false"}, {"CONNECTION_TYPE": "http"}),
    ],
    indirect=True,
)
def test_model_backup_unhappy(t4c_backup_container_parametrized):
    with pytest.raises(RuntimeError):
        conftest.wait_for_container(
            t4c_backup_container_parametrized, "Backup finished"
        )
