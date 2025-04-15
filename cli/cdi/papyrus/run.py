# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pathlib

import typer

from cdi import args, docker, git, helpers, validators
from cdi import logging as _logging
from cdi.base import args as base_args
from cdi.eclipse import args as eclipse_args
from cdi.papyrus import build as papyrus_builder

from . import args as papyrus_args

app = typer.Typer()


@app.command(
    name="papyrus",
    help="Run the Papyrus Image.",
)
def papyrus(
    *,
    image_prefix: args.ImagePrefixOption = "",
    image_tag: args.ImageTagOption = "{papyrus_version}-{cdi_revision}",
    uid: base_args.UIDOption = base_args.UID_OPTION_DEFAULT,
    push: args.PushOption = False,
    no_cache: args.NoCacheOption = False,
    papyrus_version: papyrus_args.PapyrusVersionOption = "6.4.0",
    remote: args.RemoteOption = True,
    detach: args.RunDetachedOption = False,
    memory_min: eclipse_args.MemoryMinOption = "70%",
    memory_max: eclipse_args.MemoryMaxOption = "90%",
    debug: args.DebugOption = False,
    skip_build: args.SkipBuildOption = False,
    connect_to_x_server: args.ConnectToXServerOption = False,
    workspace: args.WorkspacePathOption = None,
    rdp_password: args.RDPPasswordOption = None,
    connection_method: args.ConnectionMethodOption = args.ConnectionMethod.XPRA,
    xpra_subpath: args.XpraSubpathOption = "/xpra",
    rdp_port: args.RDPPortOption = 3390,
    xpra_port: args.XpraPortOption = 8888,
    metrics_port: args.MetricsPortOption = 9118,
    autostart_papyrus: papyrus_args.AutostartPapyrusOption = True,
    restart_papyrus: papyrus_args.RestartPapyrusOption = True,
    _verbose: _logging.VerboseOption = False,
) -> None:
    helpers.print_cli_options(locals(), "running Papyrus")

    validators.validate_x_server_connection(
        remote=remote, connect_to_x_server=connect_to_x_server
    )
    validators.validate_rdp_password_option(connection_method, rdp_password)
    validators.validate_build_architecture(docker.SupportedArchitecture.amd64)

    if not skip_build:
        papyrus_builder.papyrus(
            skip_base_image=False,
            skip_papyrus_image=False,
            image_prefix=image_prefix,
            image_tag=image_tag,
            uid=uid,
            push=push,
            no_cache=no_cache,
            papyrus_version=papyrus_version,
            remote=remote,
        )

    image = "papyrus"
    if remote:
        image += "/remote"
    image += ":" + image_tag.format(
        papyrus_version=papyrus_version,
        cdi_revision=git.get_current_cdi_revision(),
    )

    environment: dict[str, str] = {}
    ports: dict[int, int] = {}
    volumes: dict[pathlib.Path, pathlib.PurePosixPath] = {}

    environment["MEMORY_MIN"] = memory_min
    environment["MEMORY_MAX"] = memory_max

    if workspace:
        volumes[workspace] = pathlib.PurePosixPath("/workspace")

    environment["AUTOSTART_PAPYRUS"] = "1" if autostart_papyrus else "0"
    environment["RESTART_PAPYRUS"] = "1" if restart_papyrus else "0"

    helpers.configure_remote_connection(
        environment,
        ports,
        connection_method=connection_method,
        xpra_subpath=xpra_subpath,
        rdp_password=rdp_password,
        rdp_port=rdp_port,
        xpra_port=xpra_port,
    )
    helpers.configure_x_server_connection(
        environment, connect_to_x_server=connect_to_x_server
    )

    ports[metrics_port] = 9118

    docker.run_container(
        image_name=image,
        build_architecture=docker.SupportedArchitecture.amd64,
        detach=detach,
        environment=environment,
        ports=ports,
        volumes=volumes,
        debug=debug,
        after_run_callback=helpers.remote_callback_factory(
            remote=remote,
            connection_method=connection_method,
            rdp_port=rdp_port,
            xpra_port=xpra_port,
            xpra_subpath=xpra_subpath,
        ),
    )
