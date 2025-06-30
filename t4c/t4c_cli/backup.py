# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import datetime
import json
import logging
import os
import pathlib
import re
import shutil
import subprocess
import typing as t
import urllib.parse

import click
import yaml

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
    commit_history_only: bool = False,
    checkout: datetime.datetime | None = None,
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
            "-importerCredentials"
            if util_capella.is_capella_5_x_x()
            else "-repositoryCredentials"
        ),
        t4c_config.credentials_file_path,
        "-outputFolder",
        t4c_config.project_dir_path,
        "-archiveProject",
        "true",
        "-overrideExistingProject",
        "true",
        "-importCommitHistoryAsJson",
        "true",
        "-backupDBOnFailure",
        "false",
    ]

    if util_capella.is_capella_7_x_x() and commit_history_only:
        command += [
            "-importType",
            "COMMIT_HISTORY_ONLY",
        ]

    if last_backup_commit_datetime is not None:
        command += [
            "-from",
            util_datetime.format_datetime_to_isoformat_without_tz(
                last_backup_commit_datetime + datetime.timedelta(seconds=1)
            ),
            "-to",
            util_datetime.format_datetime_to_isoformat_without_tz(
                datetime.datetime.now()
            ),
        ]

    if checkout:
        command += [
            "-checkout",
            util_datetime.format_datetime_to_isoformat_without_tz(checkout),
        ]

    return command


def _validate_backup_stdout(line: str) -> None:
    if (
        re.search(r"project .+ not found on the repository .+\.", line)
        or "No project found!" in line
    ):
        log.warning(
            "Project not found in the repository."
            " This is expected if the referenced revision relates to another project in the repository.",
        )
        raise ProjectNotFoundError()
    if re.search(r"[1-9][0-9]* projects? imports? failed", line):
        raise RuntimeError("Backup failed. Please check the logs above.")
    if re.search(r"[1-9][0-9]* archivings? failed", line):
        raise RuntimeError(
            f"Failed to create archives in output folder ({config.config.t4c.project_dir_path})"
        )


def fetch_t4c_commit_history(
    last_backup_commit_datetime: datetime.datetime | None,
) -> None:
    util_capella.run_capella_command_and_handle_errors(
        "com.thalesgroup.mde.melody.collab.importer",
        _build_backup_command(
            last_backup_commit_datetime, commit_history_only=True
        ),
    )


class ProjectNotFoundError(Exception):
    """Exception if the TeamForCapella project is not found"""


def run_importer_script(
    last_backup_commit_datetime: datetime.datetime | None = None,
    checkout: datetime.datetime | None = None,
) -> None:
    log.debug("Import model from TeamForCapella server...")

    stdout, _ = util_capella.run_capella_command_and_handle_errors(
        "com.thalesgroup.mde.melody.collab.importer",
        _build_backup_command(last_backup_commit_datetime, checkout=checkout),
        _validate_backup_stdout,
    )

    if util_capella.is_capella_5_0_x():
        if not re.search(r"!MESSAGE [1-9][0-9]* Succeeded", stdout):
            raise RuntimeError(
                "'!MESSAGE [1-9][0-9]* Succeeded' not found in logs"
            )
    else:
        if not re.search(r"[1-9][0-9]* projects? imports? succeeded", stdout):
            raise RuntimeError(
                "'[1-9][0-9]* projects? imports? succeeded' not found in logs"
            )
        if not re.search(r"[1-9][0-9]* archivings? succeeded", stdout):
            raise RuntimeError(
                "'[1-9][0-9]* archivings? succeeded' not found in logs"
            )

    log.info("Import of model from TeamForCapella server finished")


def unzip_exported_files() -> None:
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

    log.info("Finished copying files...")


def clean_and_create_t4c_project_dir() -> None:
    """Remove all files in the t4c project directory or create it if it does not exist.

    We can't simply remove the directory because it could be mounted as a volume.
    """

    project_dir = pathlib.Path(config.config.t4c.project_dir_path)
    if project_dir.exists():
        for item in project_dir.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
    else:
        project_dir.mkdir(exist_ok=True)


class CommitHistoryEntry(t.TypedDict):
    description: str
    date: datetime.datetime
    user: str


def get_activities_from_history() -> list[CommitHistoryEntry]:
    commit_history = next(
        pathlib.Path(config.config.t4c.project_dir_path).glob(
            "CommitHistory__*.json*"
        )
    )

    with commit_history.open(encoding="utf-8") as file:
        commit_history_json = json.load(file)

    return [
        {
            "description": activity.get("description") or "No commit message",
            "date": datetime.datetime.fromisoformat(activity["date"]),
            "user": activity.get("user") or "Unknown",
        }
        for activity in commit_history_json["activityMetadataExport"][
            "activities"
        ]
    ]


def run_importer_and_local() -> None:
    """Run the import locally and extract the project files"""

    run_importer_script()
    unzip_exported_files()

    log.info("Backup of model finished (stored locally)")


def grouped_git_commits(
    last_backup_commit_datetime: datetime.datetime | None = None,
) -> None:
    """Create one Git commit for all T4C activities since the last backup"""
    run_importer_script(last_backup_commit_datetime)
    unzip_exported_files()

    activities = get_activities_from_history()
    if len(activities) == 0:
        log.info("No new commits since last backup")
        return

    commit_information = yaml.dump(activities, sort_keys=False)

    copy_exported_files_into_git_repo()
    util_git.git_commit_and_push(
        git_config=config.config.git,
        commit_message=f"[CDI] Backup\n\n{commit_information}",
        commit_datetime=activities[0]["date"],
    )

    log.info("Backup of model finished with grouped commit mapping")


def exact_git_commit_mapping(
    last_backup_commit_datetime: datetime.datetime | None = None,
) -> None:
    """Create individual Git commits for each T4C activity since the last backup"""

    fetch_t4c_commit_history(
        last_backup_commit_datetime=last_backup_commit_datetime
    )
    activities = get_activities_from_history()

    if len(activities) == 0:
        log.info("No new commits since last backup")
        return

    if len(activities) > 20:
        log.warning(
            "Too many commits for the exact commit mapping. Falling back to grouped commit mapping."
        )
        grouped_git_commits(last_backup_commit_datetime)
        return

    log.info("Found %s commits since last backup", len(activities))

    for idx, activity in enumerate(activities[::-1]):
        log.info(
            "Starting to export the following commit (%d/%d):"
            "\nDate: %s"
            "\nDescription: %s"
            "\nUser: %s",
            idx,
            len(activities),
            activity["date"],
            activity["description"],
            activity["user"],
        )

        if activity["date"] == last_backup_commit_datetime:
            log.info(
                "Skipping commit '%s' from '%s', already committed",
                activity["description"],
                activity["date"],
            )
            continue

        clean_and_create_t4c_project_dir()
        try:
            run_importer_script(checkout=activity["date"])
        except ProjectNotFoundError:
            log.warning(
                "Project not found in the repository for commit %s."
                " Continue with next commit.",
                activity["date"],
            )
            continue
        unzip_exported_files()
        copy_exported_files_into_git_repo()

        util_git.git_commit_and_push(
            git_config=config.config.git,
            author=activity["user"],
            commit_message=f"[CDI] {activity['description']}",
            commit_datetime=activity["date"],
        )

    log.info("Backup of model finished with exact commit mapping")


@click.command()
def backup() -> None:
    git_config: config.GitConfig = config.config.git
    file_handler = config.config.file_handler

    clean_and_create_t4c_project_dir()
    util_git.init_git()

    if file_handler == config.FileHandler.LOCAL:
        run_importer_and_local()
        return

    util_git.clone_git_repository_to_git_dir_path()

    last_backup_commit_datetime = (
        util_git.find_last_commit_timestamp_by_text_search(
            git_config=git_config, grep_arg=r"\[CDI\]"
        )
    )
    if not last_backup_commit_datetime:
        # Legacy backup commits don't have the [CDI] tag
        last_backup_commit_datetime = (
            util_git.find_last_commit_timestamp_by_text_search(
                git_config=git_config, grep_arg="Backup"
            )
        )

    log.info(
        "The last backup Git commit was on %s",
        last_backup_commit_datetime,
    )

    if config.config.commit_mapping == config.CommitMapping.EXACT and (
        not util_capella.is_capella_7_x_x()
    ):
        log.warning(
            "Exact commit mapping is only supported with Capella 7.x.x and later."
            " Fallback to grouped commits."
        )

    if (
        config.config.commit_mapping == config.CommitMapping.EXACT
        and util_capella.is_capella_7_x_x()
    ):
        exact_git_commit_mapping(last_backup_commit_datetime)
        return

    grouped_git_commits(last_backup_commit_datetime)
    return


if __name__ == "__main__":
    backup()
