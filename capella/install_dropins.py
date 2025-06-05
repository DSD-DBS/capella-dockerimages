# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import os
import pathlib
import subprocess
import typing as t
import urllib.request

import yaml


def load_dropins() -> dict[str, t.Any]:
    dropins_path = pathlib.Path("/opt/dropins.yml")
    dropins_overwrites_path = pathlib.Path("/opt/dropins.overwrites.yml")

    dropins = yaml.safe_load(dropins_path.read_text(encoding="utf-8"))["dropins"]
    dropins_overwrites = {}
    if dropins_overwrites_path.exists():
        dropins_overwrites_content = yaml.safe_load(
            dropins_overwrites_path.read_text(encoding="utf-8")
        )
        if "dropins" in dropins_overwrites_content:
            dropins_overwrites = dropins_overwrites_content["dropins"]

    return dropins | dropins_overwrites


def extract_repositories_and_install_ius(dropins: dict[str, t.Any]) -> None:
    dropins_to_install = os.getenv("CAPELLA_DROPINS", "").split(",") + [
        dropin[0] for dropin in dropins.items() if dropin[1].get("autouse")
    ]

    for dropin_slug in dropins_to_install:
        if not dropin_slug:
            continue

        if dropin_slug not in dropins:
            raise KeyError(
                f"Dropin '{dropin_slug}' not found in list of supported dropins."
            )

        dropin = dropins[dropin_slug]

        proxy = "{proxy}"
        if "proxy" in dropin:
            proxy = dropin["proxy"]

        if isinstance(proxy, str):
            proxy = proxy.format(proxy=os.getenv("HTTPS_PROXY", ""))

        match dropin["type"]:
            case "updateSite":
                install_update_sites(
                    resolve_repositories(dropin["eclipseRepository"]),
                    dropin["installIU"],
                    dropin.get("tag"),
                    dropin.get("profile"),
                    proxy,
                    dropin.get("disable_mirrors", False),
                )
            case "dropin":
                download_and_copy_dropin(dropin["downloadURL"], dropin["fileName"])
            case _:
                raise ValueError(f"Unknown plugin type '{dropin['type']}'.")


def resolve_repositories(repositories: list[str] | str) -> list[str]:
    if isinstance(repositories, str):
        return [repositories]
    elif isinstance(repositories, list):
        return repositories
    else:
        raise TypeError(
            f"Expected 'repositories' to be a string or list, got {type(repositories)}."
        )


def transform_repository(repository: str) -> str:
    if any(repository.startswith(prefix) for prefix in ("http://", "https://", "jar:")):
        return repository
    elif repository.endswith(".zip"):
        return f"jar:file:///opt/patches/{repository}!/"
    else:
        raise ValueError(
            f"Unsupported repository format: {repository}. Must be a URL or a zip file."
        )


def install_update_sites(
    repositories: list[str],
    install_iu: list[str],
    tag: str | None,
    profile: str | None,
    proxy: str | None = None,
    disable_mirrors: bool = False,
) -> None:
    repositories_command = []
    for repository in repositories:
        repositories_command += ["-repository", transform_repository(repository)]

    additional_params = []
    if tag:
        additional_params += ["-tag", tag]
    if profile:
        additional_params += ["-profile", profile]

    vm_args = []
    if disable_mirrors:
        vm_args = ["-vmargs", "-Declipse.p2.mirrors=false"]

    command = [
        "/opt/capella/capella",
        "-consoleLog",
        "-application",
        "org.eclipse.equinox.p2.director",
        "-noSplash",
        *repositories_command,
        *additional_params,
        "-installIU",
        ",".join(install_iu),
    ]
    env = {}

    if proxy:
        env["http_proxy"] = proxy
        env["https_proxy"] = proxy

    print(f"Running command: {' '.join(command)}")

    process = subprocess.Popen(
        [
            "/opt/capella/capella",
            "-consoleLog",
            "-application",
            "org.eclipse.equinox.p2.director",
            "-noSplash",
            *repositories_command,
            "-installIU",
            ",".join(install_iu),
            *vm_args,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env,
    )

    if process.stdout:
        for line in iter(process.stdout.readline, b""):
            decoded_line = line.decode("utf-8")
            if "DEBUG org.apache.hc.client5" not in decoded_line:
                print(decoded_line, end="")

    exit_code = process.wait()
    if exit_code != 0:
        raise subprocess.CalledProcessError(exit_code, command)


def download_and_copy_dropin(download_url: str, file_name: str) -> None:
    urllib.request.urlretrieve(
        download_url, pathlib.Path("/opt/capella/dropins") / file_name
    )


if __name__ == "__main__":
    loaded_dropins = load_dropins()
    extract_repositories_and_install_ius(loaded_dropins)
