# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json
import logging
import os
import pathlib
import re
import shutil
import typing as t

from lxml import etree
from lxml.builder import E

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger("pure::variants preparation")

WORKSPACE_DIR = os.getenv("WORKSPACE_DIR", "/workspace")
ECLIPSE_SETTINGS_BASE_PATH = pathlib.Path(
    f"{WORKSPACE_DIR}/.metadata/.plugins/org.eclipse.core.runtime/.settings"
)


class ResolvedServer(t.TypedDict):
    name: str
    url: str


def replace_config(path: pathlib.Path, key: str, value: str) -> None:
    """Replace the existing config or add the config."""
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


def extract_pure_variants_major_version(version: str) -> str:
    version = os.environ["PURE_VARIANTS_VERSION"]

    pattern = r"[0-9]\.*[0-9]\.*[0-9]*"
    if not re.match(pattern, version):
        raise RuntimeError(
            f"The value of $PURE_VARIANTS_VERSION doesn't match the pattern {pattern}"
        )

    return version.split(".")[0]


def copy_license_file_to_right_location() -> None:
    source = pathlib.Path("/inputs/pure-variants/license.lic")

    if source.exists():
        LOGGER.info("License file was found.")
        major_version = extract_pure_variants_major_version(
            os.environ["PURE_VARIANTS_VERSION"]
        )
        destination = pathlib.Path(
            f"/home/techuser/pure-variants-{major_version}/de.license"
        )
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
    else:
        LOGGER.warning(
            "No license file was found."
            "Please mount the file as volume to /inputs/pure-variants/license.lic"
        )


def set_pure_variants_license_server_url() -> None:
    replace_config(
        ECLIPSE_SETTINGS_BASE_PATH / "com.ps.consul.eclipse.ui.float.prefs",
        "licenseServerLocation",
        os.environ["PURE_VARIANTS_LICENSE_SERVER"],
    )


def decode_bytes_to_eclipse_format(xml: bytes) -> str:
    return xml.decode("utf-8").replace("=", r"\=").replace(":", r"\:")


def set_pure_variants_server_url() -> None:
    known_servers = os.environ["PURE_VARIANTS_KNOWN_SERVERS"]
    if not known_servers:
        LOGGER.info(
            "PURE_VARIANTS_KNOWN_SERVERS environment variable not set."
            "Will not inject KNOWN_SERVERS into the workspace."
        )
    resolved_servers: list[ResolvedServer] = json.loads(known_servers)

    category_servers = E.servers(
        *[
            E.server(
                name=server["name"],
                description="",
                category="com.ps.consul.pvserver.model",
                url=server["url"],
            )
            for server in resolved_servers
        ]
    )

    replace_config(
        ECLIPSE_SETTINGS_BASE_PATH / "com.ps.consul.eclipse.ui.prefs",
        "CATEGORY_SERVERS",
        r'<?xml version\="1.0" encoding\="UTF-8"?>'
        + decode_bytes_to_eclipse_format(etree.tostring(category_servers)),
    )

    known_cores = E.CORELIST(
        *[E.CORE(NAME=server["name"], URL=server["url"]) for server in resolved_servers]
    )
    replace_config(
        ECLIPSE_SETTINGS_BASE_PATH / "com.ps.consul.eclipse.ui.prefs",
        "KNOWN_CORES",
        r'<?xml version\="1.0" encoding\="UTF-8" standalone\="no"?>'
        + decode_bytes_to_eclipse_format(etree.tostring(known_cores)),
    )


if __name__ == "__main__":
    LOGGER.info("Prepare Workspace...")

    set_pure_variants_license_server_url()
    copy_license_file_to_right_location()
    set_pure_variants_server_url()
