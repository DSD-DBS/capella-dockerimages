# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t

import typer

JUPYTER_RUN_OPTIONS = "Jupyter Run Options"

IMAGE_TAG_DEFAULT = "python-3.11-{cdi_revision}"

JupyterBaseURLOption = t.Annotated[
    str,
    typer.Option(
        help="Base URL for Jupyter.",
        envvar="JUPYTER_BASE_URL",
        rich_help_panel=JUPYTER_RUN_OPTIONS,
    ),
]

JupyterPortOption = t.Annotated[
    int,
    typer.Option(
        help="Jupyter port on the host system.",
        envvar="WEB_PORT",
        rich_help_panel=JUPYTER_RUN_OPTIONS,
    ),
]

JupyterAdditionalDependenciesOption = t.Annotated[
    str,
    typer.Option(
        help=(
            "A space-separated list of additional pip dependencies to install."
            " The variable is passed to the 'pip install -U' command and may include additional flags."
            " The value is not escaped, only use trusted values."
        ),
        envvar="JUPYTER_ADDITIONAL_DEPENDENCIES",
        rich_help_panel=JUPYTER_RUN_OPTIONS,
    ),
]
