# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t

import typer

PAPYRUS_OPTIONS = "Papyrus Options"

PapyrusVersionOption = t.Annotated[
    str,
    typer.Option(
        help="Semantic Version of the Papyrus client to use",
        envvar="PAPYRUS_VERSION",
        rich_help_panel=PAPYRUS_OPTIONS,
    ),
]

SkipPapyrusImageOption = t.Annotated[
    bool,
    typer.Option(
        "--skip-papyrus-image",
        help=(
            "Skip the build of the Papyrus image."
            " Use this option if you already have a pre-built Capella image"
            " that you want to extend."
        ),
        rich_help_panel=PAPYRUS_OPTIONS,
    ),
]

AutostartPapyrusOption = t.Annotated[
    bool,
    typer.Option(
        "--autostart-papyrus",
        help="Automatically start Papyrus. If disabled, Papyrus has be started manually.",
        envvar="AUTOSTART_PAPYRUS",
        rich_help_panel=PAPYRUS_OPTIONS,
    ),
]

RestartPapyrusOption = t.Annotated[
    bool,
    typer.Option(
        "--restart-papyrus",
        help=(
            "Automatically restart Papyrus after termination of the application."
            " If disabled, Papyrus will not start again when closed."
        ),
        envvar="RESTART_PAPYRUS",
        rich_help_panel=PAPYRUS_OPTIONS,
    ),
]
