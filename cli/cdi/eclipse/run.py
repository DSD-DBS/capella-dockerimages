# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pathlib

import typer

from cdi import args, docker, helpers, validators
from cdi import logging as _logging
from cdi.base import args as base_args
from cdi.eclipse import args as eclipse_args
from cdi.eclipse import build as eclipse_builder
from cdi.pure_variants import args as pv_args
from cdi.pure_variants import run as pv_runner

app = typer.Typer()


@app.command(
    name="eclipse",
    help="Run the Eclipse Image, including pure::variants or remote support.",
)
def eclipse(
    *,
    detach: args.RunDetachedOption = False,
    root: args.RunAsRootOption = False,
    memory_min: eclipse_args.MemoryMinOption = "70%",
    memory_max: eclipse_args.MemoryMaxOption = "90%",
    debug: args.DebugOption = False,
    skip_build: args.SkipBuildOption = False,
    cpu_architecture: args.CPUArchitectureOption,
    image_prefix: args.ImagePrefixOption = "",
    image_tag: args.ImageTagOption = "{eclipse_version}-{cdi_revision}",
    uid: base_args.UIDOption = base_args.UID_OPTION_DEFAULT,
    push: args.PushOption = False,
    no_cache: args.NoCacheOption = False,
    eclipse_version: eclipse_args.EclipseVersionOption = "4.27",
    remote: args.RemoteOption = True,
    pure_variants_client: pv_args.PureVariantsOption = False,
    pure_variants_version: pv_args.PureVariantsVersionOption = "6.0.1",
    connect_to_x_server: args.ConnectToXServerOption = False,
    workspace: args.WorkspacePathOption = None,
    autostart_eclipse: eclipse_args.AutostartEclipseOption = True,
    restart_eclipse: eclipse_args.RestartEclipseOption = True,
    rdp_password: args.RDPPasswordOption = None,
    connection_method: args.ConnectionMethodOption = args.ConnectionMethod.XPRA,
    xpra_subpath: args.XpraSubpathOption = "/xpra",
    rdp_port: args.RDPPortOption = 3390,
    xpra_port: args.XpraPortOption = 8888,
    metrics_port: args.MetricsPortOption = 9118,
    pv_license_server: pv_args.PureVariantsLicenseServerOption = "http://localhost:8080",
    pv_known_servers: pv_args.PureVariantsKnownServersOption = '[{"name": "test", "url": "http://example.localhost"}]',
    pv_lic_file_path: pv_args.PureVariantsLicenseFilePath = pathlib.Path(
        "./volumes/pure-variants/license.lic"
    ),
    _verbose: _logging.VerboseOption = False,
) -> None:
    helpers.print_cli_options(locals(), "running Eclipse")

    validators.validate_x_server_connection(
        remote=remote, connect_to_x_server=connect_to_x_server
    )
    validators.validate_rdp_password_option(connection_method, rdp_password)

    if not skip_build:
        eclipse_builder.eclipse(
            skip_base_image=False,
            skip_eclipse_image=False,
            cpu_architecture=cpu_architecture,
            image_prefix=image_prefix,
            image_tag=image_tag,
            uid=uid,
            push=push,
            no_cache=no_cache,
            eclipse_version=eclipse_version,
            remote=remote,
            pure_variants_client=pure_variants_client,
            pure_variants_version=pure_variants_version,
        )

    image = eclipse_builder.get_final_eclipse_image_tag(
        image_prefix=image_prefix,
        image_tag=image_tag,
        eclipse_version=eclipse_version,
        pure_variants_version=pure_variants_version,
        remote=remote,
        pure_variants_client=pure_variants_client,
    )

    environment: dict[str, str] = {}
    ports: dict[int, int] = {}
    volumes: dict[pathlib.Path, pathlib.PurePosixPath] = {}

    environment["MEMORY_MIN"] = memory_min
    environment["MEMORY_MAX"] = memory_max

    if workspace:
        volumes[workspace] = pathlib.PurePosixPath("/workspace")

    environment["AUTOSTART_ECLIPSE"] = "1" if autostart_eclipse else "0"
    environment["RESTART_ECLIPSE"] = "1" if restart_eclipse else "0"

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

    pv_runner.inject_pure_variants(
        environment,
        volumes,
        pv_client=pure_variants_client,
        pv_license_server=pv_license_server,
        pv_known_servers=pv_known_servers,
        pv_lic_file_path=pv_lic_file_path,
    )

    docker.run_container(
        image_name=image,
        build_architecture=cpu_architecture,
        detach=detach,
        environment=environment,
        ports=ports,
        volumes=volumes,
        debug=debug,
        root=root,
        after_run_callback=helpers.remote_callback_factory(
            remote=remote,
            connection_method=connection_method,
            rdp_port=rdp_port,
            xpra_port=xpra_port,
            xpra_subpath=xpra_subpath,
        ),
    )
