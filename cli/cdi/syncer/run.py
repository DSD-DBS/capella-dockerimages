# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import logging
import pathlib
import typing as t

import typer
from rich import prompt

from cdi import args, docker, helpers
from cdi import logging as _logging
from cdi.base import args as base_args
from cdi.capella import args as capella_args
from cdi.capella import build as capella_builder

from . import args as syncer_args

log = logging.getLogger(__name__)

app = typer.Typer()


def file_handler_validator(
    option_name: str,
    option_value: t.Any,
    file_handler: syncer_args.FileHandler,
) -> None:
    if option_value is None:
        log.error(
            "The option '%s' is required for the file handler '%s'.",
            option_name,
            file_handler.value,
        )
        raise typer.Exit(1)


@app.command(
    name="export-to-t4c",
    help="Export a model from a Git repository or the local filesystem to a TeamForCapella server.",
)
def git2t4c(
    *,
    debug: args.DebugOption = False,
    skip_build: args.SkipBuildOption = False,
    cpu_architecture: args.CPUArchitectureOption,
    image_prefix: args.ImagePrefixOption = "",
    image_tag: args.ImageTagOption = "{capella_version}-{cdi_revision}",
    uid: base_args.UIDOption = base_args.UID_OPTION_DEFAULT,
    push: args.PushOption = False,
    no_cache: args.NoCacheOption = False,
    capella_version: capella_args.CapellaVersionOption = "7.0.0",
    build_type: capella_args.BuildTypeOption = capella_args.BuildType.OFFLINE,
    capella_download_url: capella_args.CapellaDownloadURLOption = None,
    capella_dropins: capella_args.CapellaDropinsOption = "",
    file_handler: syncer_args.FileHandlerOption = syncer_args.FileHandler.LOCAL,
    git_repo_url: syncer_args.GitRepositoryURLOption = "http://host.docker.internal:10001/git/git-test-repo.git",
    git_repo_branch: syncer_args.GitRepositoryRevisionOption = "main",
    entrypoint: syncer_args.EntrypointOption = None,
    local_path: syncer_args.LocalFileHandlerPathOption = None,
    t4c_repo_name: syncer_args.T4CRepositoryNameOption = "test-repo",
    t4c_project_name: syncer_args.T4CProjectNameOption = "test-project",
    git_username: syncer_args.GitUsernameOption = None,
    git_password: syncer_args.GitPasswordOption = None,
    t4c_server_host: syncer_args.T4CServerHostOption = "host.docker.internal",
    t4c_server_port: syncer_args.T4CServerPortOption = 2036,
    t4c_username: syncer_args.T4CUsername = "admin",
    t4c_password: syncer_args.T4CPassword = None,
    _verbose: _logging.VerboseOption = False,
) -> None:
    helpers.print_cli_options(locals(), "running T4C Exporter")

    if file_handler == syncer_args.FileHandler.LOCAL:
        file_handler_validator("--local-path", local_path, file_handler)
    else:
        file_handler_validator("--git-repo-url", git_repo_url, file_handler)
        file_handler_validator(
            "--git-repo-branch", git_repo_branch, file_handler
        )

        if git_username is None:
            log.warning(
                "No Git username provided."
                " Make sure that the repository is public!"
                " Proceeding without authentication..."
            )
        elif git_password is None:
            git_password = prompt.Prompt.ask(
                f":key: Enter the password of the source [bold]Git repository[/bold] for user '{git_username}'",
                password=True,
            )

            if not git_password:
                log.warning(
                    "No Git password provided. Proceeding without authentication...",
                )

    while not t4c_password:
        t4c_password = prompt.Prompt.ask(
            f":key: Enter the password for the [bold]TeamForCapella server[/bold] for user '{t4c_username}'",
            password=True,
            show_default=False,
        )
        if not t4c_password:
            log.error(
                "No TeamForCapella password provided. Try again...",
            )

    source_text = (
        f"local directory '{local_path}'"
        if file_handler == syncer_args.FileHandler.LOCAL
        else f"Git repository '{git_repo_url}' on branch '{git_repo_branch}'"
    )
    result = prompt.Confirm.ask(
        f":star2: Do you want to export the project {t4c_project_name} from the {source_text}"
        f" to the TeamForCapella repository '{t4c_repo_name}' on the server '{t4c_server_host}:{t4c_server_port}'?",
    )
    if not result:
        raise typer.Abort()

    if not skip_build:
        capella_builder.capella(
            skip_base_image=False,
            skip_capella_image=False,
            cpu_architecture=cpu_architecture,
            image_prefix=image_prefix,
            image_tag=image_tag,
            uid=uid,
            push=push,
            no_cache=no_cache,
            capella_version=capella_version,
            remote=False,
            t4c_client=True,
            build_type=build_type,
            capella_download_url=capella_download_url,
            capella_dropins=capella_dropins,
            install_old_gtk_version=False,
            pure_variants_client=False,
        )

    image = capella_builder.get_final_capella_tag(
        image_prefix=image_prefix,
        image_tag=image_tag,
        capella_version=capella_version,
        pure_variants_version=None,
        t4c_client=True,
        remote=False,
        pure_variants_client=False,
    )

    environment: dict[str, str] = {}
    ports: dict[int, int] = {}
    volumes: dict[pathlib.Path, pathlib.PurePosixPath] = {}

    environment["FILE_HANDLER"] = file_handler.value
    environment["ENTRYPOINT"] = entrypoint or ""
    if file_handler == syncer_args.FileHandler.LOCAL:
        assert local_path is not None
        volumes[local_path] = pathlib.PurePosixPath("/tmp/data")
    else:
        assert git_repo_url is not None
        environment["GIT_REPO_URL"] = git_repo_url
        environment["GIT_REPO_BRANCH"] = git_repo_branch
        environment["GIT_USERNAME"] = git_username or ""
        environment["GIT_PASSWORD"] = git_password or ""

    environment["T4C_REPO_HOST"] = t4c_server_host
    environment["T4C_REPO_PORT"] = str(t4c_server_port)
    environment["T4C_REPO_NAME"] = t4c_repo_name
    environment["T4C_PROJECT_NAME"] = t4c_project_name
    environment["T4C_USERNAME"] = t4c_username
    environment["T4C_PASSWORD"] = t4c_password

    if debug:
        volumes[pathlib.Path("./t4c/t4c_cli")] = pathlib.PurePosixPath(
            "/opt/.venv/lib/python3.11/site-packages/t4c_cli"
        )

    docker.run_container(
        image_name=image,
        build_architecture=cpu_architecture,
        detach=False,
        environment=environment,
        ports=ports,
        volumes=volumes,
        debug=debug,
        args=["export"],
    )


@app.command(
    name="import-from-t4c",
    help="Import a model from a TeamForCapella server to a Git repository or the local filesystem.",
)
def t4c2git(
    *,
    debug: args.DebugOption = False,
    skip_build: args.SkipBuildOption = False,
    cpu_architecture: args.CPUArchitectureOption,
    image_prefix: args.ImagePrefixOption = "",
    image_tag: args.ImageTagOption = "{capella_version}-{cdi_revision}",
    uid: base_args.UIDOption = base_args.UID_OPTION_DEFAULT,
    push: args.PushOption = False,
    no_cache: args.NoCacheOption = False,
    capella_version: capella_args.CapellaVersionOption = "7.0.0",
    build_type: capella_args.BuildTypeOption = capella_args.BuildType.OFFLINE,
    capella_download_url: capella_args.CapellaDownloadURLOption = None,
    capella_dropins: capella_args.CapellaDropinsOption = "",
    file_handler: syncer_args.FileHandlerOption = syncer_args.FileHandler.LOCAL,
    git_repo_url: syncer_args.GitRepositoryURLOption = "http://host.docker.internal:10001/git/git-test-repo.git",
    git_repo_branch: syncer_args.GitRepositoryRevisionOption = "main",
    entrypoint: syncer_args.EntrypointOption = None,
    local_path: syncer_args.LocalFileHandlerPathOption = None,
    t4c_repo_name: syncer_args.T4CRepositoryNameOption = "test-repo",
    t4c_project_name: syncer_args.T4CProjectNameOption = "test-project",
    git_username: syncer_args.GitUsernameOption = None,
    git_password: syncer_args.GitPasswordOption = None,
    t4c_server_host: syncer_args.T4CServerHostOption = "host.docker.internal",
    t4c_server_port: syncer_args.T4CServerPortOption = 2036,
    t4c_username: syncer_args.T4CUsername = "admin",
    t4c_password: syncer_args.T4CPassword = None,
    _verbose: _logging.VerboseOption = False,
) -> None:
    helpers.print_cli_options(locals(), "running T4C Importer")

    if file_handler == syncer_args.FileHandler.LOCAL:
        file_handler_validator("--local-path", local_path, file_handler)
    else:
        file_handler_validator("--git-repo-url", git_repo_url, file_handler)
        file_handler_validator(
            "--git-repo-branch", git_repo_branch, file_handler
        )

        if git_username is None:
            log.error("You have to provide a Git username.")
            raise typer.Exit(1)

        if git_password is None:
            git_password = prompt.Prompt.ask(
                f":key: Enter the password of the target [bold]Git repository[/bold] for user '{git_username}'",
                password=True,
            )

            if not git_password:
                log.error("The Git password is required.")
                raise typer.Exit(1)

    while not t4c_password:
        t4c_password = prompt.Prompt.ask(
            f":key: Enter the password for the [bold]TeamForCapella server[/bold] for user '{t4c_username}'",
            password=True,
            show_default=False,
        )
        if not t4c_password:
            log.error(
                "No TeamForCapella password provided. Try again...",
            )

    target_text = (
        f"local directory '{local_path}'"
        if file_handler == syncer_args.FileHandler.LOCAL
        else f"Git repository '{git_repo_url}' on branch '{git_repo_branch}'"
    )
    result = prompt.Confirm.ask(
        f":star2: Do you want to import the project {t4c_project_name}"
        f" from the TeamForCapella repository '{t4c_repo_name}' on the server '{t4c_server_host}:{t4c_server_port}'"
        f" to the {target_text}?",
    )
    if not result:
        raise typer.Abort()

    if not skip_build:
        capella_builder.capella(
            skip_base_image=False,
            skip_capella_image=False,
            cpu_architecture=cpu_architecture,
            image_prefix=image_prefix,
            image_tag=image_tag,
            uid=uid,
            push=push,
            no_cache=no_cache,
            capella_version=capella_version,
            remote=False,
            t4c_client=True,
            build_type=build_type,
            capella_download_url=capella_download_url,
            capella_dropins=capella_dropins,
            install_old_gtk_version=False,
            pure_variants_client=False,
        )

    image = capella_builder.get_final_capella_tag(
        image_prefix=image_prefix,
        image_tag=image_tag,
        capella_version=capella_version,
        pure_variants_version=None,
        t4c_client=True,
        remote=False,
        pure_variants_client=False,
    )

    environment: dict[str, str] = {}
    ports: dict[int, int] = {}
    volumes: dict[pathlib.Path, pathlib.PurePosixPath] = {}

    environment["FILE_HANDLER"] = file_handler.value
    environment["ENTRYPOINT"] = entrypoint or ""
    if file_handler == syncer_args.FileHandler.LOCAL:
        assert local_path is not None
        volumes[local_path] = pathlib.PurePosixPath("/tmp/model")
    else:
        assert git_repo_url is not None
        environment["GIT_REPO_URL"] = git_repo_url
        environment["GIT_REPO_BRANCH"] = git_repo_branch
        environment["GIT_USERNAME"] = git_username or ""
        environment["GIT_PASSWORD"] = git_password or ""

    environment["T4C_REPO_HOST"] = t4c_server_host
    environment["T4C_REPO_PORT"] = str(t4c_server_port)
    environment["T4C_REPO_NAME"] = t4c_repo_name
    environment["T4C_PROJECT_NAME"] = t4c_project_name
    environment["T4C_USERNAME"] = t4c_username
    environment["T4C_PASSWORD"] = t4c_password

    if debug:
        volumes[pathlib.Path("./t4c/t4c_cli")] = pathlib.PurePosixPath(
            "/opt/.venv/lib/python3.11/site-packages/t4c_cli"
        )

    docker.run_container(
        image_name=image,
        build_architecture=cpu_architecture,
        detach=False,
        environment=environment,
        ports=ports,
        volumes=volumes,
        debug=debug,
        args=["backup"],
    )
