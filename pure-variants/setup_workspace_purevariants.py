# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import logging
import os
import pathlib
import re
import shutil

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger("pure::variants preparation")

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
    if re.search(pattern, file_content):
        LOGGER.info("Set existing config %s to %s", key, value)
        file_content = re.sub(pattern, f"{key}={value}", file_content)
    else:
        file_content += f"\n{key}={value}"

    path.write_text(file_content)


def copy_license_file_to_right_location():
    source = pathlib.Path("/inputs/pure-variants/license.lic")
    if source.exists():
        LOGGER.info("License file was found.")
        destination = pathlib.Path("/home/techuser/pure-variants-5/de.license")
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
    else:
        LOGGER.warning(
            "No license file was found."
            "Please mount the file as volume to /inputs/pure-variants/license.lic"
        )


if __name__ == "__main__":
    LOGGER.info("Prepare Workspace...")

    replace_config(
        eclipse_settings_base_path / "com.ps.consul.eclipse.ui.float.prefs",
        "licenseServerLocation",
        os.getenv("PURE_VARIANTS_LICENSE_SERVER"),
    )

    copy_license_file_to_right_location()
