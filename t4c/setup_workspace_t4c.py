# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json
import logging
import os
import pathlib
import re
from collections import Counter

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger("TeamForCapella preparation")

WORKSPACE_DIR = os.getenv("WORKSPACE_DIR", "/workspace")
OBEO_COLLAB_CONF = pathlib.Path(
    f"{WORKSPACE_DIR}/.metadata",
    ".plugins/org.eclipse.core.runtime/.settings/fr.obeo.dsl.viewpoint.collab.prefs",
)
REPOSITORIES_BASE_PATH = pathlib.Path("/opt/capella/configuration")


def replace_config(path: pathlib.Path, key: str, value: str) -> None:
    """Replace the existing config or add the config option."""
    path.parent.mkdir(exist_ok=True, parents=True)
    if path.exists():
        file_content = path.read_text()
    else:
        file_content = ""

    pattern = f"{key}=.+"
    if re.search(pattern, file_content):
        LOGGER.info("Set existing config %s to %s", key, value)
        file_content = re.sub(pattern, f"{key}={value}", file_content)
    else:
        file_content += f"\n{key}={value}"

    path.write_text(file_content)


def inject_t4c_connection_details(
    key: str, protocol: str, host: str, port: str | int, repository: str
) -> None:
    replace_config(
        REPOSITORIES_BASE_PATH
        / "fr.obeo.dsl.viewpoint.collab"
        / "repository.properties",
        key,
        rf"{protocol}\://{host}\:{port}/{repository}",
    )


def setup_repositories() -> None:
    t4c_json = os.getenv("T4C_JSON", None)

    if not t4c_json:
        t4c_repositories: list[str] = os.getenv("T4C_REPOSITORIES", "").split(
            ","
        )
        t4c_host = os.getenv("T4C_SERVER_HOST", "localhost")
        t4c_port = os.getenv("T4C_SERVER_PORT", "2036")
        for repository in t4c_repositories:
            inject_t4c_connection_details(
                repository, "tcp", t4c_host, t4c_port, repository
            )
        return

    t4c_repos: list[dict[str, str]] = json.loads(t4c_json)
    if not t4c_repos:
        return

    duplicate_names = [
        name
        for name, count in Counter(
            [repo["repository"] for repo in t4c_repos]
        ).items()
        if count > 1
    ]
    for repo in t4c_repos:
        protocol = repo["protocol"] if "protocol" in repo else None
        if protocol:
            assert protocol in ["tcp", "ssl", "ws", "wss"]
        inject_t4c_connection_details(
            (
                f"{repo['repository']}\\ ({repo['instance']})"
                if repo["repository"] in duplicate_names
                else repo["repository"]
            ),
            protocol or "tcp",
            repo["host"],
            repo["port"],
            repo["repository"],
        )


if __name__ == "__main__":
    LOGGER.info("Prepare Workspace...")
    # Set default T4C Server IP address
    replace_config(
        OBEO_COLLAB_CONF,
        "PREF_DEFAULT_REPOSITORY_LOCATION",
        os.getenv("T4C_SERVER_HOST", "localhost"),
    )

    # Set default repositories in selection dialog
    setup_repositories()
