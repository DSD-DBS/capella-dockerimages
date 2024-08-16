# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import logging
import os
import pathlib
import re
import shutil

import click

from .util import capella as util_capella
from .util import config
from .util import git as util_git
from .util import t4c as util_t4c

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
log = logging.getLogger("Exporter")


def _check_capella_version() -> None:
    if util_capella.is_capella_5_x_x():
        raise RuntimeError("Operation is not supported for Capella 5.x.x")


def _build_export_command(model_dir: pathlib.Path) -> list[str]:
    t4c_config = config.config.t4c

    return [
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
        "-repositoryCredentials",
        t4c_config.credentials_file_path,
        "-sourceToExport",
        str(model_dir),
    ]


def _validate_exporter_stdout(line: str) -> None:
    if "No address associated with hostname" in line:
        raise RuntimeError("Unknown host")
    elif "No such user:" in line:
        raise RuntimeError("Unknown user")
    elif re.search(r"[1-9][0-9]* projects? exports? failed", line):
        raise RuntimeError("Export failed")


def run_exporter_script(model_dir: pathlib.Path) -> None:
    log.debug("Export model to TeamForCapella server...")

    util_capella.run_capella_command_and_handle_errors(
        "com.thalesgroup.mde.melody.collab.exporter",
        _build_export_command(model_dir),
        _validate_exporter_stdout,
    )


@click.command()
def export() -> None:
    _check_capella_version()

    root_path = pathlib.Path(os.getenv("ROOT_PATH", "/tmp/data"))
    if config.config.file_handler == config.FileHandler.GIT:
        root_path = util_git.clone_git_repository_to_git_dir_path(
            raise_if_branch_not_exist=True
        )

    model_dir = util_capella.determine_model_dir(
        root_path=root_path,
        entrypoint=config.config.git.entrypoint,
        create_if_not_exist=False,
    )

    util_t4c.check_dir_for_aird_files(model_dir)

    project_dir = pathlib.Path(f"/tmp/{config.config.t4c.project_name}")
    shutil.copytree(model_dir, project_dir)

    run_exporter_script(project_dir)

    log.info("Export of model to TeamForCapella server finished")


if __name__ == "__main__":
    export()
