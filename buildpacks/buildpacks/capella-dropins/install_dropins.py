# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import os
import pathlib
import subprocess
import typing as t
import urllib.request

import yaml

CAPELLA_VERSION = os.environ["CAPELLA_VERSION"]


def load_dropins() -> dict[str, t.Any]:
    return yaml.safe_load(
        pathlib.Path(
            "/app/capella/versions", CAPELLA_VERSION, "dropins.yml"
        ).read_text(encoding="utf-8")
    )["dropins"]


def extract_repositories_and_install_ius(dropins: dict[str, t.Any]) -> None:
    for dropin_slug in os.getenv("CAPELLA_DROPINS", "").split(","):
        if not dropin_slug:
            continue

        if not dropin_slug in dropins:
            raise KeyError(
                f"Dropin '{dropin_slug}' not found in list of supported dropins."
            )

        dropin = dropins[dropin_slug]

        match dropin["type"]:
            case "updateSite":
                install_update_sites(
                    dropin["eclipseRepository"], dropin["installIU"]
                )
            case "dropin":
                download_and_copy_dropin(
                    dropin["downloadURL"], dropin["fileName"]
                )
            case _:
                raise ValueError(f"Unknown plugin type '{dropin['type']}'.")


def install_update_sites(repository: str, install_ui: list[str]) -> None:
    subprocess.run(
        [
            "/layers/capella/app/capella",
            "-consoleLog",
            "-application",
            "org.eclipse.equinox.p2.director",
            "-noSplash",
            "-repository",
            repository,
            "-installIU",
            ",".join(install_ui),
        ],
        check=True,
    )


def download_and_copy_dropin(download_url: str, file_name: str) -> None:
    urllib.request.urlretrieve(
        download_url,
        pathlib.Path("/layers/capella/app/dropins") / file_name,
    )


if __name__ == "__main__":
    loaded_dropins = load_dropins()
    extract_repositories_and_install_ius(loaded_dropins)
