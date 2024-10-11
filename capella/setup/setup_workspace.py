# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import logging
import os
import pathlib
import re

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger("Capella preparation")

WORKSPACE_DIR = os.getenv("WORKSPACE_DIR", "/workspace")
ECLIPSE_SETTINGS_BASE_PATH = pathlib.Path(
    f"{WORKSPACE_DIR}/.metadata/.plugins/org.eclipse.core.runtime/.settings"
)


def _replace_config(path: pathlib.Path, key: str, value: str) -> None:
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
        LOGGER.info("Add new config %s with value %s", key, value)
        file_content_lines = file_content.splitlines()
        if file_content_lines and file_content_lines[-1] != "":
            file_content += "\n"
        file_content += f"{key}={value}\n"

    path.write_text(file_content)


def _set_git_merge_mode() -> None:
    """Set the default merge mode for Git to 'Last head (unmerged)'.

    The default merge strategy is set to "Working tree (pre-merged to 'Ours')"
    in the Linux bundle. This strategy has caused problems with the EMF Diff/Merge tool.
    In these cases, the Diff/Merge editor crashed with error messages like
    IndexOutOfBoundsException and "Cannot compare models".
    EMF Diff/Merge as shown to be much more stable when the option was set to "Last head (unmerged)"

    The configuration is also available in the UI:
    MacOS: Capella > Settings > Version Control (Team) > Git > Diff/Merge > Merge tool content
    Linux: Windows > Preferences > Version Control (Team) > Git > Merge tool content
    """
    _replace_config(
        ECLIPSE_SETTINGS_BASE_PATH / "org.eclipse.egit.ui.prefs",
        "merge_mode",
        "2",
    )


if __name__ == "__main__":
    # Disable Welcome Screen
    _replace_config(
        ECLIPSE_SETTINGS_BASE_PATH / "org.eclipse.ui.prefs",
        "showIntro",
        "false",
    )

    # Set default EGit path to /workspace/git
    _replace_config(
        ECLIPSE_SETTINGS_BASE_PATH / "org.eclipse.egit.core.prefs",
        "core_defaultRepositoryDir",
        f"{WORKSPACE_DIR}/git",
    )

    _set_git_merge_mode()
