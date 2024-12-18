# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import dataclasses
import enum
import os


def str_to_bool(value: str) -> bool:
    return value.lower() in ("true", "1")


class GitConfig:
    dir_path: str = "/tmp/git"
    repo_url: str = os.getenv("GIT_REPO_URL", "")
    branch: str = os.getenv("GIT_REPO_BRANCH", "")
    entrypoint: str | None = os.getenv("ENTRYPOINT") or os.getenv(
        "GIT_REPO_ENTRYPOINT"
    )
    email: str = os.getenv("GIT_EMAIL", "backup@example.com")
    username: str = os.getenv("GIT_USERNAME", "")
    password: str = os.getenv("GIT_PASSWORD", "")
    askpass: str = "/etc/git_askpass.py"


class T4CConfig:
    project_dir_path: str = "/tmp/model"
    project_name: str = os.environ["T4C_PROJECT_NAME"]
    repo_host: str = os.environ["T4C_REPO_HOST"]
    repo_port: str = os.getenv("T4C_REPO_PORT", "2036")
    repo_name: str = os.environ["T4C_REPO_NAME"]
    credentials_file_path: str = "/tmp/t4c_credentials"
    include_commit_history = str_to_bool(
        os.getenv("INCLUDE_COMMIT_HISTORY", "false")
    )

    def __init__(self) -> None:
        with open(self.credentials_file_path, "w", encoding="utf-8") as file:
            file.write(
                f"{os.environ['T4C_USERNAME']}:{os.environ['T4C_PASSWORD']}"
            )


class CapellaConfig:
    version: str = os.getenv("CAPELLA_VERSION", "")


class FileHandler(enum.Enum):
    GIT = "GIT"
    LOCAL = "LOCAL"


@dataclasses.dataclass
class GeneralConfig:
    file_handler = FileHandler(os.getenv("FILE_HANDLER", "GIT").upper())

    git: GitConfig = dataclasses.field(default_factory=GitConfig)
    t4c: T4CConfig = dataclasses.field(default_factory=T4CConfig)
    capella: CapellaConfig = dataclasses.field(default_factory=CapellaConfig)


config = GeneralConfig()
