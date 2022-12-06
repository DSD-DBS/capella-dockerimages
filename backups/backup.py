# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import itertools
import logging
import os
import pathlib
import shutil
import subprocess
import urllib.parse

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
log = logging.getLogger("Importer")


def run_importer_script() -> None:
    log.debug("Import model from TeamForCapella server...")
    subprocess.run(
        [
            "/opt/capella/capella",
            "--launcher.suppressErrors",
            "-consoleLog",
            "-data",
            "importer-workspace",
            "-application",
            "com.thalesgroup.mde.melody.collab.importer",
            "-closeserveronfailure",
            "false",
            "-hostname",
            os.environ["T4C_REPO_HOST"],
            "-port",
            os.getenv("T4C_REPO_PORT", "2036"),
            "-reponame",
            os.environ["T4C_REPO_NAME"],
            "-projectName",
            urllib.parse.quote(os.environ["T4C_PROJECT_NAME"]),
            "-importerLogin",
            os.environ["T4C_USERNAME"],
            "-importerPassword",
            os.environ["T4C_PASSWORD"],
            "-outputFolder",
            "/tmp/model",
            "-archiveProject",
            "false",
            "-importCommitHistoryAsJson",
            "true",
            "-includeCommitHistoryChanges",
            os.getenv("INCLUDE_COMMIT_HISTORY", "true"),
            "-consoleport",
            os.getenv("T4C_CDO_PORT", "12036"),
        ],
        check=True,
        cwd="/opt/capella",
    )
    log.info("Import of model from TeamForCapella server finished")


def checkout_git_repository() -> pathlib.Path:
    git_dir = pathlib.Path("/tmp/git")
    git_dir.mkdir(exist_ok=True)

    log.debug("Cloning git repository...")
    subprocess.run(
        ["git", "clone", os.environ["GIT_REPO_URL"], "/tmp/git"],
        check=True,
        env={
            "GIT_USERNAME": os.getenv("GIT_USERNAME", ""),
            "GIT_PASSWORD": os.getenv("GIT_PASSWORD", ""),
            "GIT_ASKPASS": "/etc/git_askpass.py",
        },
    )
    try:
        subprocess.run(
            ["git", "switch", os.environ["GIT_REPO_BRANCH"]],
            check=True,
            cwd=git_dir,
        )
    except subprocess.CalledProcessError as e:
        print(e.returncode)
        if e.returncode == 128:
            subprocess.run(
                ["git", "switch", "-c", os.environ["GIT_REPO_BRANCH"]],
                check=True,
                cwd=git_dir,
            )
        else:
            raise e

    log.debug("Clone of git repository finished")
    return git_dir


def copy_exported_files_into_git_repo(model_dir: pathlib.Path) -> None:
    if entrypoint := os.getenv("GIT_REPO_ENTRYPOINT", None):
        target_directory = pathlib.Path("/tmp/git", entrypoint).parent
        target_directory.mkdir(exist_ok=True, parents=True)
    else:
        target_directory = pathlib.Path(
            "/tmp/git",
        )

    for file in model_dir.glob("*/*"):
        shutil.copy2(file, target_directory)

    if os.getenv("INCLUDE_COMMIT_HISTORY", "true") == "true":
        shutil.copy2(
            next(model_dir.glob("CommitHistory__*.activitymetadata")),
            target_directory / "CommitHistory.activitymetadata",
        )
        shutil.copy2(
            next(model_dir.glob("CommitHistory__*.json*")),
            target_directory / "CommitHistory.json",
        )


def git_commit_and_push(git_dir: pathlib.Path) -> None:
    subprocess.run(
        [
            "git",
            "config",
            "user.email",
            os.getenv("GIT_EMAIL", "backup@example.com"),
        ],
        check=True,
        cwd=git_dir,
    )
    subprocess.run(
        ["git", "config", "user.name", os.getenv("GIT_USERNAME", "Backup")],
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
        subprocess.run(
            ["git", "commit", "--message", "Backup"],
            check=True,
            cwd=git_dir,
        )

        subprocess.run(
            ["git", "push", "origin", os.environ["GIT_REPO_BRANCH"]],
            check=True,
            cwd=git_dir,
            env={
                "GIT_USERNAME": os.getenv("GIT_USERNAME", ""),
                "GIT_PASSWORD": os.getenv("GIT_PASSWORD", ""),
                "GIT_ASKPASS": "/etc/git_askpass.py",
            },
        )
    else:
        log.warning("No changes, will not commit.")


if __name__ == "__main__":
    model_dir = pathlib.Path("/tmp/model")
    model_dir.mkdir(exist_ok=True)

    run_importer_script()
    git_dir = checkout_git_repository()
    copy_exported_files_into_git_repo(model_dir)
    git_commit_and_push(git_dir)
