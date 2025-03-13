# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import logging
import typing as t

import rich
import rich.logging as rich_logging
import typer
from rich import theme as rich_theme

DOCKER_LOG_LEVEL = 15


def initialize_logging() -> None:
    console = rich.get_console()
    console.push_theme(rich_theme.Theme({"logging.level.docker": "magenta"}))

    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        handlers=[
            rich_logging.RichHandler(
                markup=True,
                show_time=False,
                console=console,
            )
        ],
    )
    logging.addLevelName(DOCKER_LOG_LEVEL, "DOCKER")


def verbose_callback(
    *,
    verbose: bool,
) -> None:
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)


VerboseOption = t.Annotated[
    bool,
    typer.Option(
        "-v",
        "--verbose",
        envvar="VERBOSE",
        help="Enable verbose output",
        callback=verbose_callback,
    ),
]
