# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import logging
import os
import pathlib
import subprocess
import typing as t

import conftest
import pytest
from docker.models import containers

log = logging.getLogger(__file__)
log.setLevel("DEBUG")

pytestmark = pytest.mark.t4c_server


@pytest.fixture(name="t4c_backup_local_env")
def fixture_t4c_backup_local_env(
    git_general_env: dict[str, str],
    t4c_general_env: dict[str, str],
    t4c_ip_addr: str,
) -> dict[str, str]:
    env: dict[str, str] = git_general_env | t4c_general_env
    env["no_proxy"] = t4c_ip_addr

    return env


@pytest.fixture(name="t4c_backup_container")
def fixture_t4c_backup_container(
    t4c_backup_local_env: dict[str, str]
) -> t.Generator[containers.Container, None, None]:
    with conftest.get_container(
        image="t4c/client/base",
        environment=t4c_backup_local_env,
        command="backup",
    ) as container:
        yield container


@pytest.mark.parametrize(
    "t4c_server_container",
    [{"init": True}],
    indirect=True,
)
def test_model_backup_happy(
    t4c_backup_container: containers.Container,
    git_ip_addr: str,
    git_http_port: str,
    tmp_path: pathlib.Path,
) -> None:
    conftest.wait_for_container(
        t4c_backup_container, "Backup of model finished"
    )

    git_path = tmp_path / "test-git-data"
    git_path.mkdir()

    if conftest.DOCKER_NETWORK == "host":
        git_ip_addr = "127.0.0.1"

    env = os.environ
    env["no_proxy"] = f"{os.getenv('no_proxy', '')},{git_ip_addr}"

    subprocess.run(
        [
            "git",
            "clone",
            f"http://{git_ip_addr}:{git_http_port}/git/git-test-repo.git",
            git_path,
        ],
        check=True,
        capture_output=True,
        env=env,
    )

    try:
        subprocess.run(
            ["git", "switch", conftest.GIT_REPO_BRANCH],
            check=True,
            cwd=git_path,
            capture_output=True,
        )
    except subprocess.CalledProcessError:
        log.debug("backup failed - backup-test branch does not exists")
        raise

    assert os.path.exists(git_path / ".project")
    assert os.path.exists(git_path / "test-project.afm")
    assert os.path.exists(git_path / "test-project.aird")
    assert os.path.exists(git_path / "test-project.capella")
