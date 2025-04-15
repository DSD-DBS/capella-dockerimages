# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import logging

import typer

from cdi import args, docker

log = logging.getLogger(__name__)


def validate_build_architecture(
    cpu_architecture: args.CPUArchitectureOption,
) -> None:
    if cpu_architecture != docker.get_current_cpu_architecture():
        log.warning(
            "Running for a different architecture than the current CPU architecture."
            " This may result in slower build and run times due to emulation."
            " If running on Apple Silicon, make sure to enable Rosetta in the Docker Desktop settings."
        )


def validate_x_server_connection(
    *, remote: bool, connect_to_x_server: bool
) -> None:
    if remote and connect_to_x_server:
        log.error(
            "The options '--remote' and '--connect-to-x-server' are mutually exclusive."
        )
        raise typer.Exit(1)


def validate_rdp_password_option(
    connection_method: args.ConnectionMethod, rdp_password: str | None
) -> None:
    if connection_method is not args.ConnectionMethod.XRDP and rdp_password:
        log.error(
            "The option '--rdp-password' is only available for the connection method 'xrdp'."
        )
        raise typer.Exit(1)
