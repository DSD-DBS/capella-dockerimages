# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import re
import subprocess


def get_current_cdi_revision() -> str:
    """Return the current CDI revision.

    If the revision is a tag, return the normalized tag name.
    If the revision is a branch, return the normalized branch name.
    If the revision is detached, return the hash.
    """
    try:
        return normalize_value_for_docker(
            subprocess.check_output(
                ["git", "describe", "--tags", "--exact-match"],
                stderr=subprocess.STDOUT,
            )
            .strip()
            .decode()
        )
    except subprocess.CalledProcessError:
        pass

    branch = (
        subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"])
        .strip()
        .decode()
    )
    if branch != "HEAD":
        return normalize_value_for_docker(branch)

    return normalize_value_for_docker(
        subprocess.check_output(["git", "rev-parse", "HEAD"]).strip().decode()
    )


def normalize_value_for_docker(value: str) -> str:
    """Normalize a value for usage in docker image names."""

    return re.sub(r"[^a-zA-Z0-9.]", "-", value)
