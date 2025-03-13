# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t

import typer

BASE_OPTIONS = "Base Image Build Options"

UIDOption = t.Annotated[
    str,
    typer.Option(
        help="UID which is used for the techuser in the Docker images.",
        envvar="TECHUSER_UID",
        rich_help_panel=BASE_OPTIONS,
    ),
]
UID_OPTION_DEFAULT = "1004370000"

BaseImageTagOption = t.Annotated[
    str,
    typer.Option(
        "--base-image-tag",
        help="Docker tag for the base image.",
        rich_help_panel=BASE_OPTIONS,
    ),
]
SkipBaseImageOption = t.Annotated[
    bool,
    typer.Option(
        "--skip-base-image",
        help=(
            "Skip the build of the base image."
            " If the option is set, the base image must be pre-built already."
        ),
        rich_help_panel=BASE_OPTIONS,
    ),
]
