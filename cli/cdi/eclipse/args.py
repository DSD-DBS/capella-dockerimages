# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t

import typer

from cdi import formatting

ECLIPSE_OPTIONS = "Eclipse Options"

MemoryMinOption = t.Annotated[
    str,
    typer.Option(
        "--min-memory",
        help=(
            "Translated to `-Xms` for absolute values and `-XX:InitialRAMPercentage`"
            " and `-XX:MinRAMPercentage` for percentage values."
            " Percentage values are calculated according to the total memory or the"
            " requested memory by the container."
            " More information in our "
            + formatting.build_rich_link(
                link="https://dsd-dbs.github.io/capella-dockerimages/eclipse/memory-options/",
                text="documentation",
            )
            + "."
        ),
        envvar="MEMORY_MIN",
        rich_help_panel=ECLIPSE_OPTIONS,
    ),
]


MemoryMaxOption = t.Annotated[
    str,
    typer.Option(
        "--max-memory",
        help=(
            "Translated to `-Xmx` for absolute values and `-XX:MaxRAMPercentage`"
            " and `-XX:MinRAMPercentage` for percentage values."
            " Percentage values are calculated according to the total memory"
            " of the system or the total memory available to the container."
            " More information in our "
            + formatting.build_rich_link(
                link="https://dsd-dbs.github.io/capella-dockerimages/eclipse/memory-options/",
                text="documentation",
            )
            + "."
        ),
        envvar="MEMORY_MAX",
        rich_help_panel=ECLIPSE_OPTIONS,
    ),
]

EclipseVersionOption = t.Annotated[
    str,
    typer.Option(
        help="Version of the Eclipse client to install",
        envvar="ECLIPSE_VERSION",
        rich_help_panel=ECLIPSE_OPTIONS,
    ),
]

AutostartEclipseOption = t.Annotated[
    bool,
    typer.Option(
        "--autostart-eclipse",
        help="Automatically start Eclipse. If disabled, Eclipse has be started manually.",
        envvar="AUTOSTART_ECLIPSE",
        rich_help_panel=ECLIPSE_OPTIONS,
    ),
]

RestartEclipseOption = t.Annotated[
    bool,
    typer.Option(
        "--restart-eclipse",
        help=(
            "Automatically restart Eclipse after termination of the application."
            " If disabled, Eclipse will not start again when closed."
        ),
        envvar="RESTART_ECLIPSE",
        rich_help_panel=ECLIPSE_OPTIONS,
    ),
]
