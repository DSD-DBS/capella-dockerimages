# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import os
import pathlib
import subprocess
import typing as t

import yaml


def load_dropins() -> dict[str, t.Any]:
    return yaml.safe_load(
        pathlib.Path("/opt/dropins.yml").read_text(encoding="utf-8")
    )["dropins"]


def extract_repositories_and_installIUs(
    dropins: dict[str, t.Any]
) -> tuple[list[str], list[str]]:
    repositories = []
    install_iu = []

    for dropin_slug in os.getenv("CAPELLA_DROPINS", "").split(","):
        if not dropin_slug:
            continue

        if not dropin_slug in dropins:
            raise KeyError(
                f"Dropin '{dropin_slug}' not found in list of supported dropins."
            )

        dropin = dropins[dropin_slug]

        repositories.append(dropin["eclipseRepository"])
        install_iu += dropin["installIU"]

    return repositories, install_iu


def install_update_sites(repositories: list[str], install_ui: list[str]):
    subprocess.run(
        [
            "/opt/capella/capella",
            "-consoleLog",
            "-application",
            "org.eclipse.equinox.p2.director",
            "-noSplash",
            "-repository",
            ",".join(repositories),
            "-installIU",
            ",".join(install_ui),
        ],
        check=True,
    )


if __name__ == "__main__":
    dropins = load_dropins()
    repositories, install_ui = extract_repositories_and_installIUs(dropins)

    if repositories:
        install_update_sites(repositories, install_ui)
