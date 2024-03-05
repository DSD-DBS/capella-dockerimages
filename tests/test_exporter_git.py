# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import logging

import conftest
import pytest
from docker.models import containers

log = logging.getLogger(__file__)
log.setLevel("DEBUG")

pytestmark = pytest.mark.t4c_server


@pytest.fixture(name="t4c_exporter_git_env")
def fixture_t4c_exporter_git_env(
    git_general_env: dict[str, str],
    t4c_general_env: dict[str, str],
    request: pytest.FixtureRequest,
) -> dict[str, str]:
    env: dict[str, str] = (
        t4c_general_env | git_general_env | {"ENTRYPOINT": conftest.ENTRYPOINT}
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
    t4c_ip_addr: str,
    t4c_http_port: str,
    init_t4c_server_repo: None,  # pylint: disable=unused-argument
    init_git_server: None,  # pylint: disable=unused-argument
) -> containers.Container:
    if conftest.is_capella_6_x_x():
        assert not conftest.get_projects_of_t4c_repository(
            t4c_ip_addr, t4c_http_port
        )

    with conftest.get_container(
        image="t4c/client/base",
        environment=t4c_exporter_git_env,
        command="export",
    ) as container:
        yield container


@pytest.mark.skipif(
    condition=conftest.is_capella_5_x_x(),
    reason="Exporter does not work for capella 5.x.x",
)
def test_export_model_happy(
    t4c_exporter_container: containers.Container,
    t4c_ip_addr: str,
    t4c_http_port: str,
):
    conftest.wait_for_container(
        t4c_exporter_container,
        "Export of model to TeamForCapella server finished",
    )

    t4c_projects: list[dict[str, str]] = (
        conftest.get_projects_of_t4c_repository(t4c_ip_addr, t4c_http_port)
    )

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
