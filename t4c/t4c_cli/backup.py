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
from t4c_cli.util import config, git, t4c, util

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
log = logging.getLogger("Importer")


def _build_backup_command(
    t4c_config: config.T4CConfig,
    last_backup_commit_datetime: datetime.datetime | None,
) -> list[str]:
    command: list[str] = [
        "/opt/capella/capella",
        "--launcher.suppressErrors",
        "-nosplash",
        "-console",
        "-consoleLog",
        "-data",
        "workspace",
        "-application",
        "com.thalesgroup.mde.melody.collab.importer",
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
            if util.is_capella_5_x_x(t4c_config)
            else "-repositoryLogin"
        ),
        t4c_config.username,
        (
            "-importerPassword"
            if util.is_capella_5_x_x(t4c_config)
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
        t4c_config.import_commit_history_as_json,
        "-includeCommitHistoryChanges",
        t4c_config.include_commit_history,
        "-backupDBOnFailure",
        "false",
    ]

    if last_backup_commit_datetime is not None:
        command += [
            "-from",
            util.format_datetime_to_t4c_format(last_backup_commit_datetime),
            "-to",
            util.format_datetime_to_t4c_format(datetime.datetime.now()),
        ]
    return command


def run_importer_script(
    general_config: config.GeneralConfig,
    last_backup_commit_datetime: datetime.datetime | None,
) -> None:
    log.debug("Import model from TeamForCapella server...")

    t4c_config = general_config.t4c_config

    command = _build_backup_command(t4c_config, last_backup_commit_datetime)

    log.info("Executing the following command: %s", " ".join(command))

    stderr = None
    stdout = ""
    with subprocess.Popen(
        command, cwd="/opt/capella", stdout=subprocess.PIPE, text=True
    ) as popen:
        assert popen.stdout
        for line in popen.stdout:
            stdout += line

            # Flush is needed, otherwise the logs are delayed
            print(line, end="", flush=True)

            # Failed imports still have exit code 0.
            # In addition, the process hangs up when these log lines appear sometimes.
            # This covers some of the error cases we experienced.

            if (
                "Team for Capella server unreachable" in line
                or "Name or service not known" in line
            ):
                raise RuntimeError(
                    f"{general_config.error_prefix} - Team for Capella server unreachable"
                )
            if re.search(r"[1-9][0-9]* projects imports failed", line):
                raise RuntimeError(
                    f"{general_config.error_prefix} - Backup failed. Please check the logs above."
                )
            if re.search(r"[1-9][0-9]* archivings failed", line):
                raise RuntimeError(
                    f"{general_config.error_prefix} - Failed to create archives in output folder ({t4c_config.project_dir_path})"
                )

        if popen.stderr:
            stderr = ""
            stderr += popen.stderr.read()

    if (return_code := popen.returncode) != 0:
        log.exception("Command failed with stderr: '%s'", stderr)
        raise RuntimeError(
            f"Capella importer failed with exit code {return_code}"
        )

    if util.is_capella_5_0_x(t4c_config):
        if not re.search(r"!MESSAGE [1-9][0-9]* Succeeded", stdout):
            raise RuntimeError(
                f"{general_config.error_prefix} - '!MESSAGE [1-9][0-9]* Succeeded' not found in logs"
            )
    else:
        if not re.search(r"[1-9][0-9]* projects imports succeeded", stdout):
            raise RuntimeError(
                f"{general_config.error_prefix} - '[1-9][0-9]* projects imports succeeded' not found in logs"
            )
        if not re.search(r"[1-9][0-9]* archivings succeeded", stdout):
            raise RuntimeError(
                f"{general_config.error_prefix} - '[1-9][0-9]* archivings succeeded' not found in logs"
            )

    log.info("Import of model from TeamForCapella server finished")


def unzip_exported_files(t4c_config: config.T4CConfig):
    project_dir = pathlib.Path(t4c_config.project_dir_path)

    log.info("Start unzipping project archive in %s", project_dir)

    project_file_to_unzip = util.get_single_file_by_t4c_pattern_or_raise(
        prefix=t4c_config.project_name,
        file_format="zip",
        root_dir=project_dir,
    )

    subprocess.run(
        ["unzip", project_file_to_unzip], check=True, cwd=project_dir
    )

    log.info("Finished unzipping %s", project_file_to_unzip)


def copy_exported_files_into_git_repo(
    general_config: config.GeneralConfig,
) -> None:
    log.info("Start copying files...")

    git_config = general_config.git_config
    t4c_config = general_config.t4c_config

    project_dir = pathlib.Path(t4c_config.project_dir_path)

    target_directory = util.determine_model_dir(
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

    if t4c_config.include_commit_history == "true":
        shutil.copy2(
            next(project_dir.glob("CommitHistory__*.activitymetadata")),
            target_directory / "CommitHistory.activitymetadata",
        )

    if t4c_config.import_commit_history_as_json == "true":
        shutil.copy2(
            next(project_dir.glob("CommitHistory__*.json*")),
            target_directory / "CommitHistory.json",
        )

    log.info("Finished copying files...")


def create_t4c_project_dir(t4c_config: config.T4CConfig):
    project_dir = pathlib.Path(t4c_config.project_dir_path)
    project_dir.mkdir(exist_ok=True)


@click.command()
def backup():
    general_config: config.GeneralConfig = config.GeneralConfig(
        error_prefix="Import of model from TeamForCapella server failed"
    )
    t4c_config: config.T4CConfig = general_config.t4c_config
    git_config: config.GitConfig = general_config.git_config

    create_t4c_project_dir(t4c_config)

    last_backup_commit_datetime = None
    if general_config.file_handler == "GIT":
        git.clone_git_repository_to_git_dir_path(general_config)
        last_backup_commit_datetime = (
            git.find_last_commit_timestamp_by_text_search(
                git_config=git_config, grep_arg="Backup"
            )
        )

    run_importer_script(general_config, last_backup_commit_datetime)
    unzip_exported_files(t4c_config)

    if general_config.file_handler == "GIT":
        copy_exported_files_into_git_repo(general_config)

        commit_message = "Backup"
        if last_backup_commit_datetime:
            t4c_commit_information, last_t4c_commit_datetime = (
                t4c.extract_t4c_commit_information(t4c_config)
            )
            commit_message += f"\n\n{t4c_commit_information}"

        git.git_commit_and_push(
            git_config=git_config,
            commit_message=commit_message,
            commit_datetime=last_t4c_commit_datetime,
        )

    log.info("Backup of model finished")


if __name__ == "__main__":
    backup()
