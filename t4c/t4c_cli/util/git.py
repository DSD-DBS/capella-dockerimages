# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import datetime
import logging
import os
import pathlib
import shutil
import subprocess

from . import config
from . import log as util_log

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
log = logging.getLogger("Git")


def clean_git_directory() -> None:
    git_dir = pathlib.Path(config.config.git.dir_path)
    if git_dir.exists():
        shutil.rmtree(git_dir)


def init_git() -> None:
    subprocess.run(
        [
            "git",
            "config",
            "--global",
            "--unset",
            "core.hooksPath",
        ],
        check=True,
    )
    subprocess.run(
        ["git", "lfs", "install"],
        check=True,
    )


def clone_git_repository_to_git_dir_path(
    raise_if_branch_not_exist: bool = False,
) -> pathlib.Path:
    git_config = config.config.git

    clean_git_directory()

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
            ["git", "switch", git_config.branch],
            check=True,
            cwd=git_dir,
            env={
                "SKIP_POST_CHECKOUT": "1",
            }
            | env,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as err:
        if raise_if_branch_not_exist:
            util_log.log_subprocess_error(
                err.returncode, err.cmd, err.stdout, err.stderr
            )
            raise RuntimeError(
                f"Couldn't switch to branch {git_config.branch} in repository {git_config.repo_url}. Check the log message above."
            ) from err

    log.debug("Clone of git repository finished")
    return git_dir


def git_commit_and_push(
    git_config: config.GitConfig,
    commit_message: str,
    commit_datetime: datetime.datetime | None,
    author: str = config.config.git.username,
) -> None:
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
            [
                "git",
                "commit",
                "--allow-empty",
                "--author",
                f"{author} <{git_config.email}>",
                "--message",
                commit_message,
            ],
            check=True,
            cwd=git_dir,
            env=git_commit_env,
        )

        subprocess.run(
            [
                "git",
                "push",
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
    """Find the timestamp of the last commit.

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
            "--format=%at",
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
