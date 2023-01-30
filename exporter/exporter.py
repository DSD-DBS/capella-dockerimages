# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import logging
import os
import pathlib
import re
import shutil
import subprocess

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
log = logging.getLogger("Exporter")

ERROR_PREFIX = "Export of model to TeamForCapella server failed"

T4C_PROJECT_NAME: str = os.environ["T4C_PROJECT_NAME"]

ENTRYPOINT: str | None = os.getenv("ENTRYPOINT", None)


def check_capella_version():
    if is_capella_5_x_x():
        raise RuntimeError(
            f"{ERROR_PREFIX} - Team for Capella 5.x.x is not supported"
        )


def checkout_git_repository() -> pathlib.Path:
    git_dir = pathlib.Path("/tmp/git")
    git_dir.mkdir(exist_ok=True)

    git_repo_url: str = os.environ["GIT_REPO_URL"]
    git_repo_branch: str = os.environ["GIT_REPO_BRANCH"]

    log.debug("Cloning git repository...")
    subprocess.run(
        ["git", "clone", git_repo_url, "/tmp/git"],
        check=True,
        env={
            "GIT_USERNAME": os.getenv("GIT_USERNAME", ""),
            "GIT_PASSWORD": os.getenv("GIT_PASSWORD", ""),
            "GIT_ASKPASS": "/etc/git_askpass.py",
        },
    )
    try:
        subprocess.run(
            ["git", "switch", git_repo_branch], check=True, cwd=git_dir
        )
    except subprocess.CalledProcessError:
        log.warning(
            "Git branch %s does not exist in repository %s",
            git_repo_branch,
            git_repo_url,
        )
        raise RuntimeError(
            f"{ERROR_PREFIX} - Branch {git_repo_branch} does not exist on repository {git_repo_url}"
        )

    log.debug("Clone of git repository finished")
    return git_dir


def determine_model_dir(root_path: pathlib.Path) -> pathlib.Path:
    model_dir: pathlib.Path = root_path
    if ENTRYPOINT:
        model_dir = pathlib.Path(
            root_path, str(pathlib.Path(ENTRYPOINT).parent).lstrip("/")
        )
    return model_dir


def check_dir_for_aird_file(path: pathlib.Path):
    aird_files = list(path.glob("*.aird"))

    if not len(aird_files) == 1:
        raise RuntimeError(
            f"{ERROR_PREFIX} - Entrypoint (if provided) or root directoy does not contain a .aird file"
        )

    if ENTRYPOINT and (
        not pathlib.Path(ENTRYPOINT).name == aird_files[0].name
    ):
        raise RuntimeError(
            f"{ERROR_PREFIX} - .aird file found in git entrypoint directory does not match git entrypoint aird"
        )


# T4C determines the project name based on the directory name
def get_model_dir_with_project_name(path: pathlib.Path) -> pathlib.Path:
    project_dir: pathlib.Path = pathlib.Path(f"/tmp/{T4C_PROJECT_NAME}")

    return shutil.copytree(path, project_dir)


def run_exporter_script(model_dir: pathlib.Path) -> None:
    t4c_repo_name = os.environ["T4C_REPO_NAME"]

    command: list[str] = [
        "/opt/capella/capella",
        "-consoleLog",
        "-data",
        "workspace",
        "-application",
        "com.thalesgroup.mde.melody.collab.exporter",
        "-closeserverOnFailure",
        "false",
        "-overrideExistingProject",
        "true",
        "-mergeDifferenceOnExistingProjects",
        "true",
        "-hostname",
        os.environ["T4C_REPO_HOST"],
        "-port",
        os.getenv("T4C_REPO_PORT", "2036"),
        "-repoName",
        t4c_repo_name,
        "-repositoryLogin",
        os.environ["T4C_USERNAME"],
        "-repositoryPassword",
        os.environ["T4C_PASSWORD"],
        "-httpLogin",
        os.environ["HTTP_LOGIN"],
        "-httpPassword",
        os.environ["HTTP_PASSWORD"],
        "-httpPort",
        os.environ["HTTP_PORT"],
        "-sourceToExport",
        str(model_dir),
    ]

    with subprocess.Popen(
        command, cwd="/opt/capella", stdout=subprocess.PIPE, text=True
    ) as popen:
        if popen.stdout:
            for line in popen.stdout:
                print(line, end="", flush=True)
                if (
                    "Team for Capella server unreachable" in line
                    or "Name or service not known" in line
                ):
                    raise RuntimeError(
                        f"{ERROR_PREFIX} - Team for Capella server unreachable"
                    )
                elif "Repository not found" in line:
                    raise RuntimeError(
                        f'{ERROR_PREFIX} - Repository "{t4c_repo_name}" does not exist'
                    )
                elif "No address associated with hostname" in line:
                    raise RuntimeError(f"{ERROR_PREFIX} - Unknown host")

    if (return_code := popen.returncode) != 0:
        raise subprocess.CalledProcessError(return_code, command)


def is_capella_5_x_x() -> bool:
    return bool(re.match(r"5.[0-9]+.[0-9]+", os.getenv("CAPELLA_VERSION", "")))


if __name__ == "__main__":
    check_capella_version()

    file_handler = os.getenv("FILE_HANDLER", "")
    if file_handler == "local":
        _root_path = pathlib.Path(os.getenv("ROOT_PATH", "/tmp/data"))
    else:  # USE GIT
        _root_path = checkout_git_repository()

    _model_dir = determine_model_dir(root_path=_root_path)

    check_dir_for_aird_file(_model_dir)
    _project_dir: pathlib.Path = get_model_dir_with_project_name(_model_dir)

    run_exporter_script(_project_dir)

    log.info("Export of model to TeamForCapella server finished")
