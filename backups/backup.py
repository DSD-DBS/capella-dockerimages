# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import logging
import os
import pathlib
import re
import shutil
import subprocess
import urllib.parse

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
log = logging.getLogger("Importer")


def run_importer_script() -> None:
    log.debug("Import model from TeamForCapella server...")

    connection_type: str = get_connection_type()

    command: list[str] = ["/opt/capella/capella"]

    if is_capella_5_x_x():
        command.append("--launcher.suppressErrors")

    command += [
        "-consoleLog",
        "-data",
        "importer-workspace",
        "-application",
        "com.thalesgroup.mde.melody.collab.importer",
        "-closeserverOnFailure",
        "false",
        "-hostname",
        os.environ["T4C_REPO_HOST"],
        "-port",
        os.getenv("T4C_REPO_PORT", "2036"),
        "-repoName",
        os.environ["T4C_REPO_NAME"],
        "-projectName",
        urllib.parse.quote(os.environ["T4C_PROJECT_NAME"]),
        "-importerLogin" if is_capella_5_x_x() else "-repositoryLogin",
        os.environ["T4C_USERNAME"],
        "-importerPassword" if is_capella_5_x_x() else "-repositoryPassword",
        os.environ["T4C_PASSWORD"],
        "-outputFolder",
        "/tmp/model",
        "-archiveProject",
        "false",
        "-importCommitHistoryAsJson",
        "true",
        "-includeCommitHistoryChanges",
        os.getenv("INCLUDE_COMMIT_HISTORY", "true"),
    ]

    if connection_type == "telnet":
        command += [
            "-consoleport",
            os.getenv("T4C_CDO_PORT", "12036"),
        ]
    else:
        http_login, http_password, http_port = get_http_envs()
        command.extend(
            [
                "-httpLogin",
                http_login,
                "-httpPassword",
                http_password,
                "-httpPort",
                http_port,
            ]
        )

    with subprocess.Popen(
        command, cwd="/opt/capella", stdout=subprocess.PIPE, text=True
    ) as popen:
        if popen.stdout:
            for line in popen.stdout:
                print(line, end="")
                if "Team for Capella server unreachable" in line:
                    raise RuntimeError(
                        "Import of model from TeamForCapella server failed - Team for Capella server unreachable"
                    )

    if (return_code := popen.returncode) != 0:
        raise subprocess.CalledProcessError(return_code, command)

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


def get_connection_type() -> str:
    default_connection_type: str = "telnet" if is_capella_5_x_x() else "http"
    connection_type: str = os.getenv(
        "CONNECTION_TYPE", default_connection_type
    )

    if connection_type not in ("telnet", "http"):
        raise ValueError(
            'CONNECTION_TYPE is only allowed to be: "telnet", "http"'
        )

    if connection_type == "http" and is_capella_5_x_x():
        raise ValueError('CONNECTION_TYPE must be "telnet" for capella 5.x.x')

    return connection_type


def is_capella_5_x_x() -> bool:
    return bool(re.match(r"5.[0-9]+.[0-9]+", os.getenv("CAPELLA_VERSION", "")))


def get_http_envs() -> tuple[str, str, str]:
    http_login = os.getenv("HTTP_LOGIN")
    http_password = os.getenv("HTTP_PASSWORD")
    http_port = os.getenv("HTTP_PORT")

    if not (http_login and http_password and http_port):
        raise ValueError(
            "HTTP_LOGIN, HTTP_PASSWORD, HTTP_PORT must be specified"
        )

    return (http_login, http_password, http_port)


if __name__ == "__main__":
    model_dir = pathlib.Path("/tmp/model")
    model_dir.mkdir(exist_ok=True)

    run_importer_script()
    git_dir = checkout_git_repository()
    copy_exported_files_into_git_repo(model_dir)
    git_commit_and_push(git_dir)
    print("Backup finished")
