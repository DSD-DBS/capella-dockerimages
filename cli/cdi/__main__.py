# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import logging
import os
import pathlib
import typing as t

import dotenv
import rich
import typer

from cdi.base import build as base_builder
from cdi.capella import build as capella_builder
from cdi.capella import run as capella_runner
from cdi.eclipse import build as eclipse_builder
from cdi.eclipse import run as eclipse_runner
from cdi.jupyter import build as jupyter_builder
from cdi.jupyter import run as jupyter_runner
from cdi.papyrus import build as papyrus_builder
from cdi.papyrus import run as papyrus_runner
from cdi.syncer import run as syncer_runner

from . import __version__, _repository_root, args, docker, validators
from . import logging as _logging

dotenv.load_dotenv()
_logging.initialize_logging()

log = logging.getLogger()


app = typer.Typer(
    help="A CLI to build and run Docker images in the MBSE context.",
    rich_markup_mode="rich",
)

builder_app = typer.Typer(
    help="Build Docker images",
)
builder_app.add_typer(base_builder.app)
builder_app.add_typer(capella_builder.app)
builder_app.add_typer(papyrus_builder.app)
builder_app.add_typer(eclipse_builder.app)
builder_app.add_typer(jupyter_builder.app)
app.add_typer(builder_app, name="build")

run_app = typer.Typer(help="Run or debug Docker images")
run_app.add_typer(capella_runner.app)
run_app.add_typer(jupyter_runner.app)
run_app.add_typer(papyrus_runner.app)
run_app.add_typer(eclipse_runner.app)
run_app.add_typer(syncer_runner.app)

app.add_typer(run_app, name="run")


def version_callback(*, value: bool) -> None:
    if value:
        rich.print(__version__)
        raise typer.Exit()


def validate_pwd() -> None:
    """Check that the CLI only runs from the root of the project."""
    if pathlib.Path(os.getcwd()) != _repository_root:
        log.error(
            "Please run this command from the root of the capella-dockerimages repository."
            " If you are in the correct directory, make sure to install the library in editable mode."
            "\nCurrent directory: %s"
            "\nExpected directory: %s",
            os.getcwd(),
            _repository_root,
        )
        raise typer.Exit(1)


@app.callback()
def common(
    cpu_architecture: args.CPUArchitectureOption,
    _version: t.Annotated[
        bool | None,
        typer.Option(
            "--version",
            is_eager=True,
            help="Print the current version",
            callback=version_callback,
        ),
    ] = None,
) -> None:
    validate_pwd()
    log.debug("Checking prerequisites...")
    docker.check_prerequisites()
    validators.validate_build_architecture(cpu_architecture)
    log.info(":white_check_mark: All prerequisites are met.")


if __name__ == "__main__":
    app()
