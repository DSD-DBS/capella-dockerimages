# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import os


class GitConfig:
    dir_path: str = "/tmp/git"
    repo_url: str = os.getenv("GIT_REPO_URL", "")
    branch: str = os.getenv("GIT_REPO_BRANCH", "")
    entrypoint: str | None = (
        os.getenv("ENTRYPOINT")
        if os.getenv("ENTRYPOINT", None)
        else os.getenv("GIT_REPO_ENTRYPOINT", None)
    )
    email: str = os.getenv("GIT_EMAIL", "backup@example.com")
    username: str = os.getenv("GIT_USERNAME", "")
    password: str = os.getenv("GIT_PASSWORD", "")
    askpass: str = "/etc/git_askpass.py"


class T4CConfig:
    capella_version: str = os.getenv("CAPELLA_VERSION", "")
    project_dir_path: str = "/tmp/model"
    project_name: str = os.environ["T4C_PROJECT_NAME"]
    repo_host: str = os.environ["T4C_REPO_HOST"]
    repo_port: str = os.getenv("T4C_REPO_PORT", "2036")
    repo_name: str = os.environ["T4C_REPO_NAME"]
    username: str = os.environ["T4C_USERNAME"]
    password: str = os.environ["T4C_PASSWORD"]
    import_commit_history_as_json: str = os.getenv(
        "INCLUDE_COMMIT_HISTORY", "false"
    )
    include_commit_history: str = os.getenv("INCLUDE_COMMIT_HISTORY", "false")


class GeneralConfig:
    file_handler: str = os.getenv("FILE_HANDLER", "GIT")
    error_prefix: str = "Import of model from TeamForCapella server failed"

    git_config: GitConfig = GitConfig()
    t4c_config: T4CConfig = T4CConfig()

    def __init__(self, error_prefix: str) -> None:
        self.error_prefix = error_prefix
