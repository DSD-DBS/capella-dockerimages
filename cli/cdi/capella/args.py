# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import enum
import typing as t

import typer

from cdi import formatting

CAPELLA_OPTIONS = "Capella Options"

T4COption = t.Annotated[
    bool,
    typer.Option(
        "--t4c-client/--without-t4c-client",
        help="Install the TeamForCapella client to the image",
        rich_help_panel=CAPELLA_OPTIONS,
    ),
]


CapellaVersionOption = t.Annotated[
    str,
    typer.Option(
        help="Version of the Capella client to install",
        envvar="CAPELLA_VERSION",
        rich_help_panel=CAPELLA_OPTIONS,
    ),
]


CAPELLA_BUILD_OPTIONS = "Capella Build Options"


class BuildType(str, enum.Enum):
    ONLINE = "online"
    OFFLINE = "offline"


BuildTypeOption = t.Annotated[
    BuildType,
    typer.Option(
        help="Download Capella client during build (online) or read from file-system (offline)",
        envvar="CAPELLA_BUILD_TYPE",
        rich_help_panel=CAPELLA_BUILD_OPTIONS,
    ),
]
CapellaDownloadURLOption = t.Annotated[
    str | None,
    typer.Option(
        help="URL to download the Capella client from. Only used if `--build-type online` is set.",
        envvar="CAPELLA_DOWNLOAD_URL",
        show_default="https://www.eclipse.org/downloads/download.php?file=/capella/core/products/releases/{}&r=1",
        rich_help_panel=CAPELLA_BUILD_OPTIONS,
    ),
]
SkipCapellaImageOption = t.Annotated[
    bool,
    typer.Option(
        "--skip-capella-image",
        help=(
            "Skip the build of the Capella image."
            " Use this option if you already have a pre-built Capella image"
            " that you want to extend."
        ),
    ),
]

CapellaDropinsOption = t.Annotated[
    str,
    typer.Option(
        help="Comma-separated list of dropins to install in the Capella client",
        envvar="CAPELLA_DROPINS",
        rich_help_panel=CAPELLA_BUILD_OPTIONS,
    ),
]

CAPELLA_RUN_OPTIONS = "Capella Run Options"

DisableSemanticBrowserOption = t.Annotated[
    bool,
    typer.Option(
        "--disable-semantic-browser-auto-refresh",
        help="Disable the semantic browser auto-refresh in Capella",
        envvar="CAPELLA_DISABLE_SEMANTIC_BROWSER_AUTO_REFRESH",
        rich_help_panel=CAPELLA_RUN_OPTIONS,
    ),
]


class LogLevel(str, enum.Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


LogLevelOption = t.Annotated[
    LogLevel,
    typer.Option(
        "--container-log-level",
        help="Set the log level of commands and applications running inside the Capella container",
        envvar="LOG_LEVEL",
        rich_help_panel=CAPELLA_RUN_OPTIONS,
    ),
]


AutostartCapellaOption = t.Annotated[
    bool,
    typer.Option(
        "--autostart-capella",
        help="Automatically start Capella. If disabled, Capella has be started manually.",
        envvar="AUTOSTART_CAPELLA",
        rich_help_panel=CAPELLA_RUN_OPTIONS,
    ),
]

RestartCapellaOption = t.Annotated[
    bool,
    typer.Option(
        "--restart-capella",
        help=(
            "Automatically restart Capella after termination of the application."
            " If disabled, Capella will not start again when closed."
        ),
        envvar="RESTART_CAPELLA",
        rich_help_panel=CAPELLA_RUN_OPTIONS,
    ),
]

CapellaArguments = t.Annotated[
    list[str] | None,
    typer.Argument(
        help=(
            "Arbitrary arguments passed to the Capella subcommand."
            " Can be used for the "
            + formatting.build_rich_link(
                link="https://github.com/eclipse-capella/capella/blob/master/doc/plugins/org.polarsys.capella.commandline.doc/html/19.%20Command%20Line%20Support/19.1.%20Core%20Mechanism%20and%20Applications.mediawiki",
                text="Capella CLI",
            )
            + "."
        ),
        rich_help_panel=CAPELLA_RUN_OPTIONS,
    ),
]

TeamForCapellaLicenseConfigurationOption = t.Annotated[
    str | None,
    typer.Option(
        "--t4c-license-configuration",
        help=(
            "License configuration string for the T4C client."
            " The license configuration is the string that is usually"
            " placed after '-DOBEO_LICENSE_SERVER_CONFIGURATION=' in the 'capella.ini' file."
        ),
        envvar="T4C_LICENCE_SECRET",
        rich_help_panel=CAPELLA_RUN_OPTIONS,
    ),
]

TeamForCapellaRepositoryListOption = t.Annotated[
    str | None,
    typer.Option(
        "--t4c-repo-json",
        help=(
            "JSON containing a list of repositories."
            " The format is described in our "
            + formatting.build_rich_link(
                text="documentation",
                link="https://dsd-dbs.github.io/capella-dockerimages/capella/t4c/base/#run-the-container",
            )
            + "."
        ),
        envvar="T4C_JSON",
        rich_help_panel=CAPELLA_RUN_OPTIONS,
    ),
]
