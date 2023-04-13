# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import logging
import mimetypes
import os
import pathlib
import re
import shutil
import subprocess
import urllib.parse

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
log = logging.getLogger("Importer")

ERROR_PREFIX: str = "Import of model from TeamForCapella server failed"

OUTPUT_FOLDER: str = "/tmp/model"


def run_importer_script() -> None:
    log.debug("Import model from TeamForCapella server...")

    connection_type: str = get_connection_type()

    command: list[str] = ["/opt/capella/capella"]

    if is_capella_5_x_x():
        command.append("--launcher.suppressErrors")

    command += [
        "-consoleLog",
        "-data",
        "workspace",
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
        OUTPUT_FOLDER,
        "-archiveProject",
        "false",
        "-importCommitHistoryAsJson",
        os.getenv("INCLUDE_COMMIT_HISTORY", "true"),
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
        command += [
            "-httpLogin",
            http_login,
            "-httpPassword",
            http_password,
            "-httpPort",
            http_port,
        ]

    stdout = ""
    try:
        popen = subprocess.Popen(
            command, cwd="/opt/capella", stdout=subprocess.PIPE, text=True
        )
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
                    f"{ERROR_PREFIX} - Team for Capella server unreachable"
                )
            if re.search(r"[1-9][0-9]* projects imports failed", line):
                raise RuntimeError(
                    f"{ERROR_PREFIX} - Backup failed. Please check the logs above."
                )
            if re.search(r"[1-9][0-9]* copies failed", line):
                raise RuntimeError(
                    f"{ERROR_PREFIX} - Failed to copy to output folder ({OUTPUT_FOLDER})"
                )
    finally:
        if popen:
            stderr = popen.stderr.read() if popen.stderr else None
            popen.terminate()

    if (return_code := popen.returncode) != 0:
        log.exception("Command failed with stderr: '%s'", stderr)
        raise RuntimeError(
            f"Capella importer failed with exit code {return_code}"
        )

    if is_capella_5_x_x():
        if not re.search(r"!MESSAGE [1-9][0-9]* Succeeded", stdout):
            raise RuntimeError(
                f"{ERROR_PREFIX} - '!MESSAGE [1-9][0-9]* Succeeded' not found in logs"
            )
    else:
        if not re.search(r"[1-9][0-9]* projects imports succeeded", stdout):
            raise RuntimeError(
                f"{ERROR_PREFIX} - '[1-9][0-9]* projects imports succeeded' not found in logs"
            )
        if not re.search(r"[1-9][0-9]* copies succeeded", stdout):
            raise RuntimeError(
                f"{ERROR_PREFIX} - '[1-9][0-9]* copies succeeded' not found in logs"
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


def unmess_file_structure(model_dir: pathlib.Path) -> None:
    """Sort images and airdfragments into folders

    The importer application of TeamForCapella places all files into the project directory,
    without sorting into the images and fragments directories.
    This function sorts '*.airdfragment' files into the fragments directory.
    Images with mimetype 'image/*' are copied into the images directory.
    """

    log.info("Start unmessing files...")

    (model_dir / "images").mkdir(exist_ok=True)
    (model_dir / "fragments").mkdir(exist_ok=True)

    for file in model_dir.iterdir():
        if file.is_file():
            mimetype = mimetypes.guess_type(file)[0]
            if file.suffix in (".airdfragment", ".capellafragment"):
                file.rename(model_dir / "fragments" / file.name)
            elif mimetype and mimetype.startswith("image/"):
                file.rename(model_dir / "images" / file.name)

    log.info("Finished unmessing files...")


def copy_exported_files_into_git_repo(project_dir: pathlib.Path) -> None:
    log.info("Start copying files...")

    if entrypoint := os.getenv("GIT_REPO_ENTRYPOINT", None):
        target_directory = pathlib.Path(
            "/tmp/git", str(pathlib.Path(entrypoint).parent).lstrip("/")
        )
        target_directory.mkdir(exist_ok=True, parents=True)
    else:
        target_directory = pathlib.Path(
            "/tmp/git",
        )

    model_dir = project_dir / urllib.parse.quote(
        os.environ["T4C_PROJECT_NAME"]
    )
    unmess_file_structure(model_dir)

    shutil.copytree(
        model_dir,
        target_directory,
        dirs_exist_ok=True,
    )

    if os.getenv("INCLUDE_COMMIT_HISTORY", "true") == "true":
        shutil.copy2(
            next(project_dir.glob("CommitHistory__*.activitymetadata")),
            target_directory / "CommitHistory.activitymetadata",
        )
        shutil.copy2(
            next(project_dir.glob("CommitHistory__*.json*")),
            target_directory / "CommitHistory.json",
        )

    log.info("Finished copying files...")


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
    _project_dir = pathlib.Path(OUTPUT_FOLDER)
    _project_dir.mkdir(exist_ok=True)

    run_importer_script()

    file_handler = os.getenv("FILE_HANDLER", "")
    if file_handler == "local":
        pass
    else:  # USE GIT
        _git_dir = checkout_git_repository()
        copy_exported_files_into_git_repo(_project_dir)
        git_commit_and_push(_git_dir)

    log.info("Import of model from TeamForCapella server finished")
