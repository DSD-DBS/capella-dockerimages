# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import enum
import pathlib
import typing as t

import typer

from cdi import docker, formatting

BUILD_OPTIONS = "General Build Options"


CPUArchitectureOption = t.Annotated[
    docker.SupportedArchitecture,
    typer.Option(
        "--cpu-architecture",
        envvar="BUILD_ARCHITECTURE",
        help="Target CPU architecture. If specified, builds may take longer due to emulation.",
        default_factory=docker.get_current_cpu_architecture,
        show_default="Current CPU architecture",
        rich_help_panel=BUILD_OPTIONS,
    ),
]

ImagePrefixOption = t.Annotated[
    str,
    typer.Option(
        envvar="DOCKER_PREFIX",
        help="Prefix for the image name",
        rich_help_panel=BUILD_OPTIONS,
    ),
]

ImageTagOption = t.Annotated[
    str,
    typer.Option(
        "-t",
        "--image-tag",
        envvar="DOCKER_TAG",
        help=(
            "Docker tag for the image. You can use variables like '{cdi_version}' in the "
            + formatting.build_rich_link(
                link="https://docs.python.org/3/library/stdtypes.html#str.format",
                text="Python f-string format",
            )
            + "."
        ),
        rich_help_panel=BUILD_OPTIONS,
    ),
]

ImageLabelOption = t.Annotated[
    list[str] | None,
    typer.Option(
        "--label",
        help="Key-value pairs of labels for Docker image in the format 'key=value'.",
        rich_help_panel=BUILD_OPTIONS,
    ),
]


PushOption = t.Annotated[
    bool,
    typer.Option(
        "-p",
        "--push",
        help="Push the built image to the Docker registry",
        envvar="PUSH_IMAGES",
        rich_help_panel=BUILD_OPTIONS,
    ),
]

NoCacheOption = t.Annotated[
    bool,
    typer.Option(
        "--no-cache",
        help="Disable the Docker cache during the build",
        rich_help_panel=BUILD_OPTIONS,
    ),
]

RemoteOption = t.Annotated[
    bool,
    typer.Option(
        help="Add support for `xrdp` and `xpra` to the image to allow remote connections into the container",
        rich_help_panel=BUILD_OPTIONS,
    ),
]


SkipBuildOption = t.Annotated[
    bool,
    typer.Option(
        help=(
            "Skip the build of the corresponding image."
            " Use this option if you already have a pre-built image."
            " Make sure that the pre-built image is up-to-date!"
        ),
        rich_help_panel=BUILD_OPTIONS,
    ),
]

RUN_OPTIONS = "General Run Options"


RunDetachedOption = t.Annotated[
    bool,
    typer.Option(
        "--detach/--interactive",
        "-d/-i",
        help="Run the image as detached.",
        rich_help_panel=RUN_OPTIONS,
    ),
]


RunAsRootOption = t.Annotated[
    bool,
    typer.Option(
        "--root/--techuser",
        help="Run the image as root user. Otherwise use the non-root techuser.",
        rich_help_panel=RUN_OPTIONS,
    ),
]


DebugOption = t.Annotated[
    bool,
    typer.Option(
        "--debug",
        help="Debug the container. Run with entrypoint bash.",
        rich_help_panel=RUN_OPTIONS,
    ),
]

ConnectToXServerOption = t.Annotated[
    bool,
    typer.Option(
        "--connect-to-x11",
        help="Run the application on an existing X11 Server on the host via TCP.",
        rich_help_panel=RUN_OPTIONS,
    ),
]


class ConnectionMethod(str, enum.Enum):
    XRDP = "xrdp"
    XPRA = "xpra"


ConnectionMethodOption = t.Annotated[
    ConnectionMethod,
    typer.Option(
        help="Connection method if remote functionality is enabled.",
        envvar="CONNECTION_METHOD",
        rich_help_panel=RUN_OPTIONS,
    ),
]

RDPPasswordOption = t.Annotated[
    str | None,
    typer.Option(
        help=(
            "RDP password for the remote connection."
            " Only required if the connection method is xrdp."
        ),
        envvar="RMT_PASSWORD",
        rich_help_panel=RUN_OPTIONS,
    ),
]

XpraSubpathOption = t.Annotated[
    str,
    typer.Option(
        help="Subpath for the XPRA connection method.",
        envvar="XPRA_SUBPATH",
        rich_help_panel=RUN_OPTIONS,
    ),
]

RDPPortOption = t.Annotated[
    int,
    typer.Option(
        help="RDP port on the host system. Only relevant if the connection method is xrdp.",
        envvar="RDP_PORT",
        rich_help_panel=RUN_OPTIONS,
    ),
]

XpraPortOption = t.Annotated[
    int,
    typer.Option(
        help="Xpra port on the host system. Only relevant if the connection method is xpra.",
        envvar="WEB_PORT",
        rich_help_panel=RUN_OPTIONS,
    ),
]

MetricsPortOption = t.Annotated[
    int,
    typer.Option(
        help="Metrics port on the host system.",
        envvar="METRICS_PORT",
        rich_help_panel=RUN_OPTIONS,
    ),
]

WorkspacePathOption = t.Annotated[
    pathlib.Path | None,
    typer.Option(
        "--workspace",
        help="Path to the workspace directory on the host system. If None, the workspace is not mounted.",
        envvar="WORKSPACE_PATH",
        rich_help_panel=RUN_OPTIONS,
        exists=True,
        file_okay=False,
        dir_okay=True,
        writable=True,
        readable=True,
    ),
]
