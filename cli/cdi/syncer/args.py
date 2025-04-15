# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import enum
import pathlib
import typing as t

import typer

GIT_OPTIONS = "Git Repository Options"
T4C_OPTIONS = "TeamForCapella Options"

T4CServerHostOption = t.Annotated[
    str,
    typer.Option(
        "--t4c-server-host",
        help=(
            "Hostname of the TeamForCapella server."
            " Instead of localhost, use 'host.docker.internal'"
        ),
        envvar="T4C_SERVER_HOST",
        rich_help_panel=T4C_OPTIONS,
    ),
]

T4CServerPortOption = t.Annotated[
    int,
    typer.Option(
        "--t4c-server-port",
        help="Port of the TeamForCapella server for TCP connections.",
        envvar="T4C_SERVER_PORT",
        rich_help_panel=T4C_OPTIONS,
    ),
]

T4CUsername = t.Annotated[
    str,
    typer.Option(
        "--t4c-username",
        help="Username of the TeamForCapella server with access to the required repository.",
        envvar="T4C_USERNAME",
        rich_help_panel=T4C_OPTIONS,
    ),
]


T4CPassword = t.Annotated[
    str | None,
    typer.Option(
        "--t4c-password",
        help="Password of the TeamForCapella user with access to the required repository.",
        envvar="T4C_PASSWORD",
        rich_help_panel=T4C_OPTIONS,
    ),
]

GitRepositoryURLOption = t.Annotated[
    str,
    typer.Option(
        "--git-repo-url",
        help=("HTTP URL of the relevant Git repository."),
        envvar="GIT_REPO_URL",
        rich_help_panel=GIT_OPTIONS,
    ),
]

GitRepositoryRevisionOption = t.Annotated[
    str,
    typer.Option(
        "--git-branch",
        help=("Branch of the Git repository."),
        envvar="GIT_REPO_BRANCH",
        rich_help_panel=GIT_OPTIONS,
    ),
]


EntrypointOption = t.Annotated[
    str | None,
    typer.Option(
        "--entrypoint",
        help=(
            "Path to the directory containing the `.project` file,"
            " relative to the Git repository root or local directory."
            " If not provided, the root directory of the repository or the provided local directory are used."
        ),
        envvar="GIT_REPO_ENTRYPOINT",
        rich_help_panel=GIT_OPTIONS,
    ),
]


T4CRepositoryNameOption = t.Annotated[
    str,
    typer.Option(
        "--t4c-repo-name",
        help="Repository name of the TeamForCapella repository.",
        envvar="T4C_REPO_NAME",
        rich_help_panel=T4C_OPTIONS,
    ),
]

T4CProjectNameOption = t.Annotated[
    str,
    typer.Option(
        "--t4c-project-name",
        help="Project name of the project in the TeamForCapella repository.",
        envvar="T4C_PROJECT_NAME",
        rich_help_panel=T4C_OPTIONS,
    ),
]

GitUsernameOption = t.Annotated[
    str | None,
    typer.Option(
        "--git-username",
        help="Git username if Git repository authentication is required.",
        envvar="GIT_USERNAME",
        rich_help_panel=GIT_OPTIONS,
    ),
]

GitPasswordOption = t.Annotated[
    str | None,
    typer.Option(
        "--git-password",
        help="Git password if Git repository authentication is required.",
        envvar="GIT_PASSWORD",
        rich_help_panel=GIT_OPTIONS,
    ),
]


class FileHandler(str, enum.Enum):
    LOCAL = "local"
    GIT = "git"


FileHandlerOption = t.Annotated[
    FileHandler,
    typer.Option(
        "--file-handler",
        help="Decide to use the local filesystem or Git as source/target.",
        rich_help_panel=GIT_OPTIONS,
    ),
]

LocalFileHandlerPathOption = t.Annotated[
    pathlib.Path | None,
    typer.Option(
        "--local-path",
        help="Path to the directory on the host filesystem for import/export if using the local file handler.",
        rich_help_panel=GIT_OPTIONS,
        exists=True,
        file_okay=False,
        dir_okay=True,
    ),
]
