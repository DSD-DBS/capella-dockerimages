# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import json
import logging
import pathlib
import re
from collections.abc import Iterator

import docker
import pytest
from docker.models import containers

from tests import conftest

log = logging.getLogger(__file__)
log.setLevel("DEBUG")
client = docker.from_env()

timeout = 120  # Timeout in seconds
default_env = {
    "T4C_LICENCE_SECRET": "",
    "RMT_PASSWORD": "my_long_password",
    "FILESERVICE_PASSWORD": "password",
    "T4C_USERNAME": "techuser",
}


@pytest.fixture(name="success_mode", params=["json", "repositories"])
def fixture_success_mode(request) -> str:
    return request.param


@pytest.fixture(
    name="container_success",
)
def fixture_container_success(
    success_mode: str,
    tmp_path: pathlib.Path,
) -> Iterator[containers.Container]:
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
    yield conftest.get_container(
        image="t4c/client/remote",
        environment=env,
        tmp_path=tmp_path,
        mount_path="/opt/capella/configuration",
    )


@pytest.fixture(name="failure_mode", params=["json"])
def fixture_failure_mode(request) -> str:
    return request.param


@pytest.fixture(name="container_failure")
def fixture_container_failure(
    failure_mode: str,
) -> Iterator[containers.Container]:
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
    yield conftest.get_container(image="t4c/client/remote", environment=env)


@pytest.mark.t4c
def test_repositories_seeding(
    container_success: Iterator[containers.Container],
    success_mode: str,
    tmp_path: pathlib.Path,
):
    tmp_path.chmod(0o777)

    container = next(container_success)
    conftest.wait_for_container(
        container, "INFO success: xrdp-sesman entered RUNNING state"
    )

    path = tmp_path / "fr.obeo.dsl.viewpoint.collab" / "repository.properties"
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
def test_invalid_env_variable(
    container_failure: Iterator[containers.Container],
):
    container = next(container_failure)
    with pytest.raises(RuntimeError):
        conftest.wait_for_container(
            container, "INFO success: xrdp-sesman entered RUNNING state"
        )
