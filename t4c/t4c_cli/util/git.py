# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import datetime
import logging
import os
import pathlib
import subprocess

from . import config

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
log = logging.getLogger("Git")


def clone_git_repository_to_git_dir_path(
    general_config: config.GeneralConfig,
    raise_if_branch_not_exist: bool = False,
) -> pathlib.Path:
    git_config = general_config.git_config

    git_dir = pathlib.Path(git_config.dir_path)
    git_dir.mkdir(exist_ok=True)

    log.debug("Cloning git repository...")
    env = {
        "GIT_USERNAME": git_config.username,
        "GIT_PASSWORD": git_config.password,
        "GIT_ASKPASS": git_config.askpass,
    }

    subprocess.run(
        [
            "git",
            "clone",
            "--filter=blob:none",
            git_config.repo_url,
            git_config.dir_path,
        ],
        check=True,
        cwd=git_dir,
        env=env,
    )

    try:
        subprocess.run(
            ["git", "switch", git_config.branch], check=True, cwd=git_dir
        )
    except subprocess.CalledProcessError:
        if raise_if_branch_not_exist:
            log.warning(
                "Git branch %s does not exist in repository %s",
                git_config.branch,
                git_config.repo_url,
            )
            raise RuntimeError(
                f"{general_config.error_prefix} - Branch {git_config.branch} does not exist on repository {git_config.repo_url}"
            )

    log.debug("Clone of git repository finished")
    return git_dir


def git_commit_and_push(
    git_config: config.GitConfig,
    commit_message: str,
    commit_datetime: datetime.datetime | None,
):
    git_dir = pathlib.Path(git_config.dir_path)

    subprocess.run(
        ["git", "config", "user.email", git_config.email],
        check=True,
        cwd=git_dir,
    )
    subprocess.run(
        ["git", "config", "user.name", git_config.username],
        check=True,
        cwd=git_dir,
    )

    subprocess.run(
        ["git", "add", "."],
        check=True,
        cwd=git_dir,
    )

    diff_returncode = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        check=False,
        cwd=git_dir,
    ).returncode

    if diff_returncode == 1:
        git_commit_env = None
        if commit_datetime is not None:
            git_commit_env = {
                "GIT_AUTHOR_DATE": commit_datetime.isoformat(),
                "GIT_COMITTER_DATE": commit_datetime.isoformat(),
            }

        subprocess.run(
            ["git", "commit", "--no-verify", "--message", commit_message],
            check=True,
            cwd=git_dir,
            env=git_commit_env,
        )

        subprocess.run(
            [
                "git",
                "push",
                "--no-verify",
                "origin",
                f"HEAD:{git_config.branch}",
            ],
            check=True,
            cwd=git_dir,
            env={
                "GIT_USERNAME": git_config.username,
                "GIT_PASSWORD": git_config.password,
                "GIT_ASKPASS": git_config.askpass,
            },
        )
    else:
        log.warning("No changes, will not commit.")


def find_last_commit_timestamp_by_text_search(
    git_config: config.GitConfig, grep_arg: str
) -> datetime.datetime | None:
    """
    Find the timestamp of the last commit that matches a given text search pattern.

    Parameters
    ----------
        git_config : config.GitConfig
            The Git configuration.
        grep_arg : str
            The text search pattern to match.

    Returns
    -------
        datetime.datetime or None
            The timestamp of the last matching commit, or None if no matching commit is found.
    """

    git_dir = pathlib.Path(git_config.dir_path)

    result = subprocess.run(
        [
            "git",
            "log",
            "-1",
            "--format=%ct",
            f"--grep={grep_arg}",
        ],
        check=False,
        capture_output=True,
        text=True,
        cwd=git_dir,
    )
    if result.returncode == 0 and result.stdout.strip():
        return datetime.datetime.fromtimestamp(
            int(result.stdout.strip()), tz=datetime.UTC
        )
    return None
