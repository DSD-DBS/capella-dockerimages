# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
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


def extract_repositories_and_installIUs(dropins: dict[str, t.Any]) -> None:
    for dropin_slug in os.getenv("CAPELLA_DROPINS", "").split(","):
        if not dropin_slug:
            continue

        if not dropin_slug in dropins:
            raise KeyError(
                f"Dropin '{dropin_slug}' not found in list of supported dropins."
            )

        dropin = dropins[dropin_slug]

        install_update_sites(dropin["eclipseRepository"], dropin["installIU"])


def install_update_sites(repository: str, install_ui: list[str]):
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
            ",".join(install_ui),
        ],
        check=True,
    )


if __name__ == "__main__":
    dropins = load_dropins()
    extract_repositories_and_installIUs(dropins)
