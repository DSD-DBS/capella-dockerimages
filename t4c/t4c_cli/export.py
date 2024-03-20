# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import logging
import os
import pathlib
import shutil
import subprocess

import click
from t4c_cli.util import config, git, t4c, util

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
log = logging.getLogger("Exporter")


def _check_capella_version(general_config: config.GeneralConfig):
    if util.is_capella_5_x_x(general_config.t4c_config):
        raise RuntimeError(
            f"{general_config.error_prefix} - Team for Capella 5.x.x is not supported"
        )


def _build_export_command(
    t4c_config: config.T4CConfig, model_dir: pathlib.Path
) -> list[str]:
    return [
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
        t4c_config.repo_host,
        "-port",
        t4c_config.repo_port,
        "-repoName",
        t4c_config.repo_name,
        "-repositoryLogin",
        t4c_config.username,
        "-repositoryPassword",
        t4c_config.password,
        "-sourceToExport",
        str(model_dir),
    ]


def run_exporter_script(
    general_config: config.GeneralConfig, model_dir: pathlib.Path
):
    log.debug("Export model to TeamForCapella server...")

    command = _build_export_command(general_config.t4c_config, model_dir)

    log.info("Executing the following command: %s", " ".join(command))

    error_prefix = general_config.error_prefix
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
                        f"{error_prefix} - Team for Capella server unreachable"
                    )
                elif "Repository not found" in line:
                    raise RuntimeError(
                        f'{error_prefix} - Repository "{general_config.t4c_config.repo_name}" does not exist'
                    )
                elif "No address associated with hostname" in line:
                    raise RuntimeError(f"{error_prefix} - Unknown host")
                elif "No such user:" in line:
                    raise RuntimeError(f"{error_prefix} - Unknown user")
                elif "1 projects exports failed" in line:
                    raise RuntimeError(f"{error_prefix} - Export failed")

    if (return_code := popen.returncode) != 0:
        raise subprocess.CalledProcessError(return_code, command)


@click.command()
def export():
    general_config: config.GeneralConfig = config.GeneralConfig(
        error_prefix="Export of model to TeamForCapella server failed"
    )
    git_config: config.GitConfig = general_config.git_config
    t4c_config: config.T4CConfig = general_config.t4c_config

    _check_capella_version(general_config)

    root_path = pathlib.Path(os.getenv("ROOT_PATH", "/tmp/data"))
    if general_config.file_handler == "GIT":
        root_path = git.clone_git_repository_to_git_dir_path(
            general_config=general_config, raise_if_branch_not_exist=True
        )

    model_dir = util.determine_model_dir(
        root_path=root_path,
        entrypoint=git_config.entrypoint,
        create_if_not_exist=False,
    )

    t4c.check_dir_for_aird_files(general_config, model_dir)

    project_dir = pathlib.Path(f"/tmp/{t4c_config.project_name}")
    shutil.copytree(model_dir, project_dir)

    run_exporter_script(general_config, project_dir)

    log.info("Export of model to TeamForCapella server finished")


if __name__ == "__main__":
    export()
