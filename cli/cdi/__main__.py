# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import logging
import os
import pathlib
import typing as t

import dotenv
import rich
import typer

from . import __version__, _repository_root, build, run, scan
from . import logging as _logging

dotenv.load_dotenv()
_logging.initialize_logging()

log = logging.getLogger()


app = typer.Typer(
    help="A CLI to build, run and scan Docker images in the MBSE context."
)
app.add_typer(build.app, name="build")
app.add_typer(run.app, name="run")
app.add_typer(scan.app, name="scan")


def version_callback(*, value: bool):
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


if __name__ == "__main__":
    app()
