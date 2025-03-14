# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import os
import pathlib
import subprocess
import typing as t
import urllib.request

import yaml


def load_dropins() -> dict[str, t.Any]:
    return yaml.safe_load(pathlib.Path("/opt/dropins.yml").read_text(encoding="utf-8"))[
        "dropins"
    ]


def extract_repositories_and_install_ius(dropins: dict[str, t.Any]) -> None:
    for dropin_slug in os.getenv("CAPELLA_DROPINS", "").split(","):
        if not dropin_slug:
            continue

        if dropin_slug not in dropins:
            raise KeyError(
                f"Dropin '{dropin_slug}' not found in list of supported dropins."
            )

        dropin = dropins[dropin_slug]

        match dropin["type"]:
            case "updateSite":
                install_update_sites(dropin["eclipseRepository"], dropin["installIU"])
            case "dropin":
                download_and_copy_dropin(dropin["downloadURL"], dropin["fileName"])
            case _:
                raise ValueError(f"Unknown plugin type '{dropin['type']}'.")


def install_update_sites(repository: str, install_iu: list[str]) -> None:
    subprocess.run(
        [
            "/opt/capella/capella",
            "-consoleLog",
            "-application",
            "org.eclipse.equinox.p2.director",
            "-noSplash",
            "-repository",
            repository,
            "-installIU",
            ",".join(install_iu),
        ],
        check=True,
    )


def download_and_copy_dropin(download_url: str, file_name: str) -> None:
    urllib.request.urlretrieve(
        download_url, pathlib.Path("/opt/capella/dropins") / file_name
    )


if __name__ == "__main__":
    loaded_dropins = load_dropins()
    extract_repositories_and_install_ius(loaded_dropins)
