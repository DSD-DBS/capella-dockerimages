# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import logging
import os
import pathlib
import shutil
import subprocess
import typing as t

import conftest
import pytest
from docker.models import containers

log = logging.getLogger(__file__)
log.setLevel("DEBUG")

pytestmark = pytest.mark.t4c_server

ENTRYPOINT: str = "/test-project/test-project.aird"

SUBPROCESS_DEFAULT_ARGS: dict[str, t.Any] = {
    "check": True,
    "text": True,
    "capture_output": True,
}


@pytest.fixture(name="init_git_server")
def fixture_init_git_server(
    git_ip_addr: str, git_http_port: str, tmp_path: pathlib.Path
):
    _checkout_git_repository(git_ip_addr, git_http_port, tmp_path)
    _copy_test_project_into_git_repo(tmp_path)
    _commit_and_push_git_repo(tmp_path)
    yield


@pytest.fixture(name="t4c_exporter_git_env")
def fixture_t4c_exporter_git_env(
    git_general_env: dict[str, str],
    t4c_exporter_env: dict[str, str],
    request: pytest.FixtureRequest,
) -> dict[str, str]:
    env: dict[str, str] = (
        t4c_exporter_env | git_general_env | {"ENTRYPOINT": ENTRYPOINT}
    )

    if hasattr(request, "param"):
        env = env | request.param

    return env


# We should just use @pytest.mark.usefixtures("perpare_local_git_server")
# here, but right now there is a bug/issue that it doesn't work with
# @pytest.fixture (https://github.com/pytest-dev/pytest/issues/3664)
# So for now we have to keep it as an actual argument
@pytest.fixture(name="t4c_exporter_container")
def fixture_t4c_exporter_container(
    t4c_exporter_git_env: dict[str, str],
    t4c_http_port: str,
    init_t4c_server_repo: None,  # pylint: disable=unused-argument
    init_git_server: None,  # pylint: disable=unused-argument
) -> containers.Container:
    if conftest.is_capella_6_x_x():
        assert not conftest.get_projects_of_t4c_repository(t4c_http_port)

    with conftest.get_container(
        image="t4c/client/exporter", environment=t4c_exporter_git_env
    ) as container:
        yield container


@pytest.mark.skipif(
    condition=conftest.is_capella_5_x_x(),
    reason="Exporter does not work for capella 5.x.x",
)
def test_export_model_happy(
    t4c_exporter_container: containers.Container, t4c_http_port: str
):
    conftest.wait_for_container(
        t4c_exporter_container,
        "Export of model to TeamForCapella server finished",
    )

    t4c_projects: list[
        dict[str, str]
    ] = conftest.get_projects_of_t4c_repository(t4c_http_port)

    assert len(t4c_projects) == 1

    t4c_project: dict[str, str] = t4c_projects[0]

    assert t4c_project["repositoryName"] == "test-repo"
    assert t4c_project["projectName"] == "test-project"
    assert t4c_project["path"] == "test-project"


@pytest.mark.skipif(
    condition=conftest.is_capella_5_x_x(),
    reason="Exporter does not work for capella 5.x.x",
)
@pytest.mark.parametrize(
    "t4c_exporter_git_env",
    [
        pytest.param(
            {"ENTRYPOINT": "/this/does/not/exist/test.aird"},
            id="invalid-entrypoint",
        ),
        pytest.param(
            {"GIT_REPO_BRANCH": "unknown-branch"}, id="unkown-branch"
        ),
        pytest.param({"T4C_REPO_HOST": "unknown"}, id="unknown-repo-host"),
        pytest.param({"T4C_REPO_NAME": "unkown"}, id="unknown-repo-name"),
    ],
    indirect=True,
)
def test_export_model_6_x_x_unhappy(
    t4c_exporter_container: containers.Container,
):
    with pytest.raises(RuntimeError):
        conftest.wait_for_container(t4c_exporter_container, "Export finished")


@pytest.mark.skipif(
    condition=conftest.is_capella_6_x_x(),
    reason="Tests checkes whether error is thrown for 5.x.x",
)
def test_export_model_5_x_x_unhappy(
    t4c_exporter_container: containers.Containe,
):
    with pytest.raises(RuntimeError):
        conftest.wait_for_container(t4c_exporter_container, "Export finished")


def _checkout_git_repository(
    git_ip_addr: str, git_http_port: str, path: pathlib.Path
):
    if conftest.DOCKER_NETWORK == "host":
        git_ip_addr = "127.0.0.1"

    env = os.environ
    env["no_proxy"] = os.getenv("no_proxy", "") + f",{git_ip_addr}"

    subprocess.run(  # pylint: disable=subprocess-run-check
        [
            "git",
            "clone",
            f"http://{git_ip_addr}:{git_http_port}/git/git-test-repo.git",
            path,
        ],
        env=env,
        **SUBPROCESS_DEFAULT_ARGS,
    )
    subprocess.run(  # pylint: disable=subprocess-run-check
        ["git", "switch", "-c", conftest.GIT_REPO_BRANCH],
        cwd=path,
        **SUBPROCESS_DEFAULT_ARGS,
    )


def _copy_test_project_into_git_repo(git_path: pathlib.Path):
    target_dir: pathlib.Path = pathlib.Path(
        git_path,
        str(pathlib.Path(ENTRYPOINT).parent).lstrip("/"),
    )
    target_dir.mkdir(exist_ok=True, parents=True)

    project_dir: pathlib.Path = (
        pathlib.Path(__file__).parents[0] / "data" / "test-project"
    )

    for file in project_dir.glob("*"):
        if not str(file).endswith("license"):
            shutil.copy2(file, target_dir)


def _commit_and_push_git_repo(path: pathlib.Path):
    subprocess_shared_args: dict[str, t.Any] = SUBPROCESS_DEFAULT_ARGS | {
        "cwd": path
    }

    subprocess.run(  # pylint: disable=subprocess-run-check
        [
            "git",
            "config",
            "user.email",
            conftest.GIT_EMAIL,
        ],
        **subprocess_shared_args,
    )

    subprocess.run(  # pylint: disable=subprocess-run-check
        ["git", "config", "user.name", conftest.GIT_USERNAME],
        **subprocess_shared_args,
    )

    subprocess.run(  # pylint: disable=subprocess-run-check
        ["git", "add", "."], **subprocess_shared_args
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
        **subprocess_shared_args,
    )

    subprocess.run(  # pylint: disable=subprocess-run-check
        ["git", "push", "origin", conftest.GIT_REPO_BRANCH],
        env={
            "GIT_USERNAME": conftest.GIT_USERNAME,
            "GIT_PASSWORD": conftest.GIT_PASSWORD,
            "GIT_ASKPASS": "/etc/git_askpass.py",
        },
        **subprocess_shared_args,
    )
