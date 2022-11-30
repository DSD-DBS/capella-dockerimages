# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import logging
import os
import pathlib
import re

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger("pure::variants")

eclipse_settings_base_path = pathlib.Path(
    "/workspace/.metadata/.plugins/org.eclipse.core.runtime/.settings"
)


def replace_config(path: pathlib.Path, key: str, value: str) -> None:
    """This will replace the existing config or add the config (if it doesn't exist)"""
    path.parent.mkdir(exist_ok=True, parents=True)
    if path.exists():
        file_content = path.read_text()
    else:
        file_content = ""

    pattern = f"{key}=.+"
    match = re.search(pattern, file_content)
    if match:
        LOGGER.info("Set existing config %s to %s", key, value)
        file_content = re.sub(pattern, f"{key}={value}", file_content)
    else:
        file_content += f"\n{key}={value}"

    path.write_text(file_content)


if __name__ == "__main__":
    LOGGER.info("Prepare Workspace...")

    replace_config(
        eclipse_settings_base_path / "com.ps.consul.eclipse.ui.float.prefs",
        "licenseServerLocation",
        os.getenv("PURE_VARIANTS_LICENSE_SERVER"),
    )

    replace_config(
        eclipse_settings_base_path / "org.eclipse.egit.core.prefs",
        "core_defaultRepositoryDir",
        "/workspace/git",
    )
