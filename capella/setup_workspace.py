# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import logging
import pathlib
import re

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger("Capella preparation")


def replace_config(path: pathlib.Path, key: str, value: str) -> None:
    """This will replace the existing config or add the config (if it doesn't exist)"""
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


if __name__ == "__main__":
    # Disable Welcome Screen
    replace_config(
        pathlib.Path(
            "/opt/capella/configuration/.settings/org.eclipse.ui.ide.prefs"
        ),
        "showIntro",
        "false",
    )

    eclipse_settings_base_path = pathlib.Path(
        "/workspace/.metadata/.plugins/org.eclipse.core.runtime/.settings"
    )
    # Set default Git path to /workspace/git
    replace_config(
        eclipse_settings_base_path / "org.eclipse.egit.core.prefs",
        "core_defaultRepositoryDir",
        "/workspace/git",
    )
