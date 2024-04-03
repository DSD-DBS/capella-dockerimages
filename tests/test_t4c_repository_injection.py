# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import json
import logging
import pathlib
import re
import typing as t

import conftest
import pytest
from docker.models import containers

log = logging.getLogger(__file__)
log.setLevel("DEBUG")

default_env = {
    "T4C_LICENCE_SECRET": "",
    "RMT_PASSWORD": "my_long_password",
    "T4C_USERNAME": "techuser",
}


@pytest.fixture(name="success_mode", params=["json", "repositories"])
def fixture_success_mode(request: pytest.FixtureRequest) -> str:
    return request.param


@pytest.fixture(
    name="container_success",
)
def fixture_container_success(
    success_mode: str,
) -> t.Generator[containers.Container, None, None]:
    env = {
        "json": {
            **default_env,
            "T4C_JSON": json.dumps(
                [
                    {
                        "repository": "name",
                        "port": 2036,
                        "host": "instance-host",
                        "instance": "dev-5.0",
                    },
                    {
                        "repository": "name",
                        "port": 2036,
                        "host": "instance-host",
                        "instance": "dev-5.2",
                    },
                    {
                        "repository": "test",
                        "port": 2036,
                        "host": "instance-host",
                    },
                ]
            ),
        },
        "repositories": {
            **default_env,
            "T4C_SERVER_HOST": "instance-host",
            "T4C_SERVER_PORT": "2036",
            "T4C_REPOSITORIES": "repo1,repo2",
        },
    }[success_mode]
    with conftest.get_container(
        image="t4c/client/remote", environment=env
    ) as container:
        yield container


@pytest.fixture(name="failure_mode", params=["json"])
def fixture_failure_mode(request: pytest.FixtureRequest) -> str:
    return request.param


@pytest.fixture(name="container_failure")
def fixture_container_failure(
    failure_mode: str,
) -> t.Generator[containers.Container, None, None]:
    env = {
        "json": {
            **default_env,
            "T4C_JSON": json.dumps(
                [
                    {
                        "repository": "duplicate-name",
                        "port": 2036,
                        "host": "instance-host",
                    },
                    {
                        "repository": "duplicate-name",
                        "port": 2036,
                        "host": "instance-host",
                    },
                    {
                        "repository": "test",
                        "port": 2036,
                        "host": "instance-host",
                    },
                ]
            ),
        },
    }[failure_mode]
    with conftest.get_container(
        image="t4c/client/remote", environment=env
    ) as container:
        yield container


@pytest.mark.t4c
def test_repositories_seeding(
    container_success: containers.Container,
    success_mode: str,
    tmp_path: pathlib.Path,
) -> None:
    tmp_path.chmod(0o777)

    conftest.wait_for_container(
        container_success, "INFO success: xrdp-sesman entered RUNNING state"
    )

    conftest.extract_container_dir_to_local_dir(
        container_success.id, "/opt/capella/configuration", tmp_path
    )

    path = (
        tmp_path
        / "configuration"
        / "fr.obeo.dsl.viewpoint.collab"
        / "repository.properties"
    )
    assert path.exists()
    file_content = path.read_text()

    if success_mode == "json":
        repositories = {
            r"name\\ \(dev-5.0\)": r"tcp\://instance-host\:2036/name",
            r"name\\ \(dev-5.2\)": r"tcp\://instance-host\:2036/name",
            r"test": r"tcp\://instance-host\:2036/test",
        }
    elif success_mode == "repositories":
        repositories = {
            r"repo1": r"tcp\://instance-host\:2036/repo1",
            r"repo2": r"tcp\://instance-host\:2036/repo2",
        }
    else:
        repositories = {}
    for key, value in repositories.items():
        findings = re.search(f"{key}=(.+)", file_content)
        assert findings
        assert value == findings.group(1)


@pytest.mark.t4c
def test_invalid_env_variable(container_failure: containers.Container) -> None:
    with pytest.raises(RuntimeError):
        conftest.wait_for_container(
            container_failure,
            "INFO success: xrdp-sesman entered RUNNING state",
        )
