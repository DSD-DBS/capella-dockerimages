# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pathlib
import typing as t

import typer

PURE_VARIANTS_BUILD_OPTIONS = "pure::variants Build Options"

PureVariantsOption = t.Annotated[
    bool,
    typer.Option(
        "--pv-client",
        help="Install the pure::variants client to the Eclipse instance in the image",
        rich_help_panel=PURE_VARIANTS_BUILD_OPTIONS,
    ),
]

PureVariantsVersionOption = t.Annotated[
    str,
    typer.Option(
        "--pv-version",
        help="Version of the pure::variants client to install",
        envvar="PURE_VARIANTS_VERSION",
        rich_help_panel=PURE_VARIANTS_BUILD_OPTIONS,
    ),
]

PURE_VARIANTS_RUN_OPTIONS = "pure::variants Run Options"

PureVariantsLicenseServerOption = t.Annotated[
    str,
    typer.Option(
        "--pv-license-server",
        help="URL of the pure::variants license server",
        envvar="PURE_VARIANTS_LICENSE_SERVER",
        rich_help_panel=PURE_VARIANTS_RUN_OPTIONS,
    ),
]

PureVariantsKnownServersOption = t.Annotated[
    str,
    typer.Option(
        "--pv-known-servers-json",
        help="Known pure::variants servers in a JSON format",
        envvar="PURE_VARIANTS_KNOWN_SERVERS",
        rich_help_panel=PURE_VARIANTS_RUN_OPTIONS,
    ),
]

PureVariantsLicenseFilePath = t.Annotated[
    pathlib.Path,
    typer.Option(
        "--lic-file-path",
        help="Path to the pure::variants `license.lic` file on the host system",
        rich_help_panel=PURE_VARIANTS_RUN_OPTIONS,
    ),
]
