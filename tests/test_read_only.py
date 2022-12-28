# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import io
import json
import logging

import conftest
import pytest
from docker.models import containers

log = logging.getLogger(__file__)
log.setLevel("DEBUG")


@pytest.fixture(name="mode_success", params=["json", "json2", "legacy"])
def fixture_mode_success(request) -> str:
    return request.param


@pytest.fixture(
    name="container_success",
)
def fixture_container_success(
    mode_success: str,
) -> containers.Container:
    env: dict[str, str] = {  # type: ignore
        "json": {
            "GIT_REPOS_JSON": json.dumps(
                [
                    {
                        "url": "https://github.com/DSD-DBS/py-capellambse.git",
                        "revision": "master",
                        "depth": 1,
                        "entrypoint": "tests/data/melodymodel/5_2/Melody Model Test.aird",
                    },
                    {
                        "url": "https://github.com/DSD-DBS/collab-platform-arch.git",
                        "revision": "main",
                        "depth": 5,
                        "entrypoint": "collab-platform-arch.aird",
                    },
                ]
            ),
        },
        # Test with starting slash in entrypoint
        "json2": {
            "GIT_REPOS_JSON": json.dumps(
                [
                    {
                        "url": "https://github.com/DSD-DBS/py-capellambse.git",
                        "revision": "master",
                        "depth": 1,
                        "entrypoint": "/tests/data/melodymodel/5_2/Melody Model Test.aird",
                    },
                ]
            ),
        },
        "legacy": {
            "GIT_URL": "https://github.com/DSD-DBS/collab-platform-arch.git",
            "GIT_ENTRYPOINT": "collab-platform-arch.aird",
            "GIT_REVISION": "main",
            "GIT_DEPTH": 0,
        },
    }[mode_success]
    with conftest.get_container(
        image="capella/readonly", environment=env
    ) as container:
        yield container


@pytest.fixture(name="mode_failure", params=["json", "legacy"])
def fixture_mode_failure(request) -> str:
    return request.param


@pytest.fixture(name="container_failure")
def fixture_container_failure(mode_failure: str) -> containers.Container:
    env: dict[str, str] = {  # type: ignore
        "json": {
            "GIT_REPOS_JSON": json.dumps(
                [
                    {
                        "url": "https://example.com/invalid-repository",
                        "revision": "main",
                        "depth": 0,
                        "entrypoint": "invalid.aird",
                    },
                ]
            ),
        },
        "legacy": {
            "GIT_URL": "https://example.com/invalid-repository",
            "GIT_ENTRYPOINT": "invalid.aird",
            "GIT_REVISION": "main",
            "GIT_DEPTH": 0,
        },
    }[mode_failure]
    with conftest.get_container(
        image="capella/readonly", environment=env
    ) as container:
        yield container


def lines(bytes):
    return io.BytesIO(bytes).readlines()


@pytest.fixture(name="workspace_result")
def fixture_workspace_result(
    container_success: containers.Container,
) -> containers.ExecResult:
    conftest.wait_for_container(container_success, "---START_SESSION---")

    return container_success.exec_run("ls -A1 /workspace")


@pytest.mark.parametrize("mode_success", ["legacy"])
def test_model_loading_with_legacy_env(
    workspace_result: containers.ExecResult,
):
    assert len(lines(workspace_result.output)) == 2


@pytest.mark.parametrize("mode_success", ["json"])
def test_model_loading_with_json_env(workspace_result: containers.ExecResult):
    assert len(lines(workspace_result.output)) == 3


@pytest.mark.parametrize("mode_success", ["json2"])
def test_model_loading_with_json2_env(workspace_result: containers.ExecResult):
    assert len(lines(workspace_result.output)) == 2


def test_invalid_url_fails(container_failure: containers.Container):
    with pytest.raises(RuntimeError):
        conftest.wait_for_container(container_failure, "---START_SESSION---")
