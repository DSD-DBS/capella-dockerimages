# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0
"""Download Capella from Eclipse download page.

Return a download URL for a stable Capella archive from the official
eclipse download page:

https://download.eclipse.org/capella/core/products/stable/.
"""
import os
import pathlib
import sys

import requests
from lxml import etree, html

CAPELLA_INDEX_URL = (
    "https://mirror.dkm.cz/eclipse/capella/core/products/releases/"
)
CAPELLA_DOWNLOAD_URL = "https://www.eclipse.org/downloads/download.php?file=/capella/core/products/releases/{}&r=1"


def get_directory_structure(url: str) -> list[str]:
    response = requests.get(url)
    response.raise_for_status()

    tree = etree.fromstring(response.content, parser=html.HTMLParser())
    return tree.xpath("//*/a/text()")


if __name__ == "__main__":
    capella_version = sys.argv[1]
    print(f"Installing Capella {capella_version}")

    if os.getenv("BUILD_ARCHITECTURE") == "arm64":
        raise RuntimeError(
            "We don't support the automatic installation of Capella on arm64 yet. "
            f"Place the Capella archive in the 'capella/versions/{capella_version}/arm64' directory in the capella-dockerimages repository, "
            "set the environment variable CAPELLA_BUILD_TYPE to 'offline' and run the build again."
        )

    versions = get_directory_structure(CAPELLA_INDEX_URL)
    capella_archive_path = next(
        version for version in versions if version.startswith(capella_version)
    )

    final_url = f"{CAPELLA_INDEX_URL}{capella_archive_path}"
    dir_content = get_directory_structure(final_url)
    archive_name = next(
        arch
        for arch in dir_content
        if arch.endswith("linux-gtk-x86_64.tar.gz")
    )
    download_url = CAPELLA_DOWNLOAD_URL.format(
        f"{capella_archive_path}{archive_name}"
    )

    download_response = requests.get(download_url)
    download_response.raise_for_status()
    download_path = pathlib.Path("/opt/capella.tar.gz").write_bytes(
        download_response.content
    )
