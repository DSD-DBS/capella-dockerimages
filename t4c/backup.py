# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import glob
import logging
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
        os.environ["T4C_REPO_HOST"],
        "-port",
        os.getenv("T4C_REPO_PORT", "2036"),
        "-repoName",
        os.environ["T4C_REPO_NAME"],
        "-projectName",
        urllib.parse.quote(os.environ["T4C_PROJECT_NAME"], safe="@"),
        "-importerLogin" if is_capella_5_x_x() else "-repositoryLogin",
        os.environ["T4C_USERNAME"],
        "-importerPassword" if is_capella_5_x_x() else "-repositoryPassword",
        os.environ["T4C_PASSWORD"],
        "-outputFolder",
        OUTPUT_FOLDER,
        "-archiveProject",
        "true",
        "-overrideExistingProject",
        "true",
        "-importCommitHistoryAsJson",
        os.getenv("INCLUDE_COMMIT_HISTORY", "true"),
        "-includeCommitHistoryChanges",
        os.getenv("INCLUDE_COMMIT_HISTORY", "true"),
        "-backupDBOnFailure",
        "false",
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
                    f"{ERROR_PREFIX} - Team for Capella server unreachable"
                )
            if re.search(r"[1-9][0-9]* projects imports failed", line):
                raise RuntimeError(
                    f"{ERROR_PREFIX} - Backup failed. Please check the logs above."
                )
            if re.search(r"[1-9][0-9]* archivings failed", line):
                raise RuntimeError(
                    f"{ERROR_PREFIX} - Failed to create archives in output folder ({OUTPUT_FOLDER})"
                )

        if popen.stderr:
            stderr = ""
            stderr += popen.stderr.read()

    if (return_code := popen.returncode) != 0:
        log.exception("Command failed with stderr: '%s'", stderr)
        raise RuntimeError(
            f"Capella importer failed with exit code {return_code}"
        )

    if is_capella_5_0_x():
        if not re.search(r"!MESSAGE [1-9][0-9]* Succeeded", stdout):
            raise RuntimeError(
                f"{ERROR_PREFIX} - '!MESSAGE [1-9][0-9]* Succeeded' not found in logs"
            )
    else:
        if not re.search(r"[1-9][0-9]* projects imports succeeded", stdout):
            raise RuntimeError(
                f"{ERROR_PREFIX} - '[1-9][0-9]* projects imports succeeded' not found in logs"
            )
        if not re.search(r"[1-9][0-9]* archivings succeeded", stdout):
            raise RuntimeError(
                f"{ERROR_PREFIX} - '[1-9][0-9]* archivings succeeded' not found in logs"
            )

    log.info("Import of model from TeamForCapella server finished")


def clone_git_repository() -> pathlib.Path:
    git_dir = pathlib.Path("/tmp/git")
    git_dir.mkdir(exist_ok=True)

    log.debug("Cloning git repository...")
    env = {
        "GIT_USERNAME": os.getenv("GIT_USERNAME", ""),
        "GIT_PASSWORD": os.getenv("GIT_PASSWORD", ""),
        "GIT_ASKPASS": "/etc/git_askpass.py",
    }

    try:
        subprocess.run(
            [
                "git",
                "clone",
                "--depth=1",
                f"--branch={os.environ['GIT_REPO_BRANCH']}",
                os.environ["GIT_REPO_URL"],
                "/tmp/git",
            ],
            check=True,
            cwd=git_dir,
            env=env,
        )
    except subprocess.CalledProcessError as e:
        if e.returncode == 128:
            subprocess.run(
                [
                    "git",
                    "clone",
                    "--depth=1",
                    os.environ["GIT_REPO_URL"],
                    "/tmp/git",
                ],
                check=True,
                cwd=git_dir,
                env=env,
            )
        else:
            raise e

    log.debug("Clone of git repository finished")
    return git_dir


def unzip_exported_files(project_dir: pathlib.Path) -> None:
    log.info("Start unzipping project archive in %s", project_dir)

    pattern = (
        f"{glob.escape(os.environ['T4C_PROJECT_NAME'])}_????????_??????.zip"
    )

    matching_files = glob.glob(pattern, root_dir=project_dir)

    if not matching_files:
        raise FileNotFoundError(f"No files found matching pattern: {pattern}")

    if len(matching_files) > 1:
        raise FileExistsError(
            f"Multiple files found matching pattern: {pattern} - {matching_files}"
        )

    project_file_to_unzip = matching_files[0]

    subprocess.run(
        ["unzip", project_file_to_unzip], check=True, cwd=project_dir
    )

    log.info("Finished unzipping %s", project_file_to_unzip)


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

    model_dir = project_dir / os.environ["T4C_PROJECT_NAME"]

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
            ["git", "push", "origin", f"HEAD:{os.environ['GIT_REPO_BRANCH']}"],
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


def is_capella_5_0_x() -> bool:
    return bool(re.match(r"5.0.[0-9]+", os.getenv("CAPELLA_VERSION", "")))


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
    unzip_exported_files(_project_dir)

    file_handler = os.getenv("FILE_HANDLER", "")
    if file_handler == "local":
        pass
    else:  # USE GIT
        _git_dir = clone_git_repository()
        copy_exported_files_into_git_repo(_project_dir)
        git_commit_and_push(_git_dir)

    log.info("Backup of model finished")
