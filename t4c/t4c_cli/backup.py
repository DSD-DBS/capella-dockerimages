# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import datetime
import logging
import os
import pathlib
import re
import shutil
import subprocess
import urllib.parse

import click

from .util import capella as util_capella
from .util import config
from .util import datetime as util_datetime
from .util import git as util_git
from .util import log as util_log
from .util import t4c as util_t4c

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
log = logging.getLogger("Importer")


def _build_backup_command(
    last_backup_commit_datetime: datetime.datetime | None,
) -> list[str]:
    t4c_config = config.config.t4c

    command: list[str] = [
        "-closeserverOnFailure",
        "false",
        "-hostname",
        t4c_config.repo_host,
        "-port",
        t4c_config.repo_port,
        "-repoName",
        t4c_config.repo_name,
        "-projectName",
        urllib.parse.quote(t4c_config.project_name, safe="@"),
        (
            "-importerLogin"
            if util_capella.is_capella_5_x_x()
            else "-repositoryLogin"
        ),
        t4c_config.username,
        (
            "-importerPassword"
            if util_capella.is_capella_5_x_x()
            else "-repositoryPassword"
        ),
        t4c_config.password,
        "-outputFolder",
        t4c_config.project_dir_path,
        "-archiveProject",
        "true",
        "-overrideExistingProject",
        "true",
        "-importCommitHistoryAsJson",
        str(t4c_config.include_commit_history),
        "-includeCommitHistoryChanges",
        str(t4c_config.include_commit_history),
        "-backupDBOnFailure",
        "false",
    ]

    if last_backup_commit_datetime is not None:
        command += [
            "-from",
            util_datetime.format_datetime_to_isoformat_without_tz(
                last_backup_commit_datetime
            ),
            "-to",
            util_datetime.format_datetime_to_isoformat_without_tz(
                datetime.datetime.now()
            ),
        ]
    return command


def _validate_backup_stdout(line: str):
    if re.search(r"[1-9][0-9]* projects imports failed", line):
        raise RuntimeError("Backup failed. Please check the logs above.")
    if re.search(r"[1-9][0-9]* archivings failed", line):
        raise RuntimeError(
            f"Failed to create archives in output folder ({config.config.t4c.project_dir_path})"
        )


def run_importer_script(
    last_backup_commit_datetime: datetime.datetime | None,
) -> None:
    log.debug("Import model from TeamForCapella server...")

    stdout, _ = util_capella.run_capella_command_and_handle_errors(
        "com.thalesgroup.mde.melody.collab.importer",
        _build_backup_command(last_backup_commit_datetime),
        _validate_backup_stdout,
    )

    if util_capella.is_capella_5_0_x():
        if not re.search(r"!MESSAGE [1-9][0-9]* Succeeded", stdout):
            raise RuntimeError(
                "'!MESSAGE [1-9][0-9]* Succeeded' not found in logs"
            )
    else:
        if not re.search(r"[1-9][0-9]* projects imports succeeded", stdout):
            raise RuntimeError(
                "'[1-9][0-9]* projects imports succeeded' not found in logs"
            )
        if not re.search(r"[1-9][0-9]* archivings succeeded", stdout):
            raise RuntimeError(
                "'[1-9][0-9]* archivings succeeded' not found in logs"
            )

    log.info("Import of model from TeamForCapella server finished")


def unzip_exported_files():
    project_dir = pathlib.Path(config.config.t4c.project_dir_path)

    log.info("Start unzipping project archive in %s", project_dir)

    project_file_to_unzip = util_t4c.get_single_file_by_t4c_pattern_or_raise(
        prefix=config.config.t4c.project_name,
        file_format="zip",
        root_dir=project_dir,
    )

    try:
        subprocess.run(
            ["unzip", project_file_to_unzip], check=True, cwd=project_dir
        )
    except subprocess.CalledProcessError as e:
        util_log.log_subprocess_error(e.returncode, e.cmd, e.stdout, e.stderr)
        raise e

    log.info("Finished unzipping %s", project_file_to_unzip)


def copy_exported_files_into_git_repo() -> None:
    log.info("Start copying files...")

    git_config = config.config.git
    t4c_config = config.config.t4c

    project_dir = pathlib.Path(t4c_config.project_dir_path)

    target_directory = util_capella.determine_model_dir(
        root_path=pathlib.Path(git_config.dir_path),
        entrypoint=git_config.entrypoint,
        create_if_not_exist=True,
    )

    model_dir = project_dir / t4c_config.project_name

    shutil.copytree(
        model_dir,
        target_directory,
        dirs_exist_ok=True,
    )

    if t4c_config.include_commit_history is True:
        shutil.copy2(
            next(project_dir.glob("CommitHistory__*.activitymetadata")),
            target_directory / "CommitHistory.activitymetadata",
        )

        shutil.copy2(
            next(project_dir.glob("CommitHistory__*.json*")),
            target_directory / "CommitHistory.json",
        )

    log.info("Finished copying files...")


def create_t4c_project_dir():
    project_dir = pathlib.Path(config.config.t4c.project_dir_path)
    project_dir.mkdir(exist_ok=True)


@click.command()
def backup():
    git_config: config.GitConfig = config.config.git
    file_handler = config.config.file_handler

    create_t4c_project_dir()

    last_backup_commit_datetime = None
    if file_handler == config.FileHandler.GIT:
        util_git.clone_git_repository_to_git_dir_path()
        last_backup_commit_datetime = (
            util_git.find_last_commit_timestamp_by_text_search(
                git_config=git_config, grep_arg="Backup"
            )
        )

    run_importer_script(last_backup_commit_datetime)
    unzip_exported_files()

    if file_handler == config.FileHandler.GIT:
        copy_exported_files_into_git_repo()

        t4c_commit_information, last_t4c_commit_datetime = (
            util_t4c.extract_t4c_commit_information()
        )

        util_git.git_commit_and_push(
            git_config=git_config,
            commit_message=f"Backup\n\n{t4c_commit_information}",
            commit_datetime=last_t4c_commit_datetime,
        )

    log.info("Backup of model finished")


if __name__ == "__main__":
    backup()
