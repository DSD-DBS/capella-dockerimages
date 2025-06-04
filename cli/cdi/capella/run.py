# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pathlib

import typer

from cdi import args, docker, helpers, validators
from cdi import logging as _logging
from cdi.base import args as base_args
from cdi.capella import args as capella_args
from cdi.capella import build as capella_builder
from cdi.eclipse import args as eclipse_args
from cdi.pure_variants import args as pv_args
from cdi.pure_variants import run as pv_runner

app = typer.Typer()


@app.command(
    name="capella",
    help="Run the Capella Image, including TeamForCapella, pure::variants, or remote support.",
)
def capella(
    *,
    detach: args.RunDetachedOption = False,
    root: args.RunAsRootOption = False,
    disable_semantic_browser: capella_args.DisableSemanticBrowserOption = False,
    log_level: capella_args.LogLevelOption = "DEBUG",  # type: ignore
    memory_min: eclipse_args.MemoryMinOption = "70%",
    memory_max: eclipse_args.MemoryMaxOption = "90%",
    debug: args.DebugOption = False,
    skip_build: args.SkipBuildOption = False,
    cpu_architecture: args.CPUArchitectureOption,
    image_prefix: args.ImagePrefixOption = "",
    image_tag: args.ImageTagOption = "{capella_version}-{cdi_revision}",
    uid: base_args.UIDOption = base_args.UID_OPTION_DEFAULT,
    push: args.PushOption = False,
    no_cache: args.NoCacheOption = False,
    capella_version: capella_args.CapellaVersionOption = "7.0.0",
    remote: args.RemoteOption = True,
    t4c_client: capella_args.T4COption = False,
    build_type: capella_args.BuildTypeOption = capella_args.BuildType.OFFLINE,
    capella_download_url: capella_args.CapellaDownloadURLOption = None,
    capella_dropins: capella_args.CapellaDropinsOption = "",
    pure_variants_client: pv_args.PureVariantsOption = False,
    pure_variants_version: pv_args.PureVariantsVersionOption = "6.0.1",
    connect_to_x_server: args.ConnectToXServerOption = False,
    workspace: args.WorkspacePathOption = None,
    autostart_capella: capella_args.AutostartCapellaOption = True,
    restart_capella: capella_args.RestartCapellaOption = True,
    rdp_password: args.RDPPasswordOption = None,
    connection_method: args.ConnectionMethodOption = args.ConnectionMethod.XPRA,
    xpra_subpath: args.XpraSubpathOption = "/xpra",
    rdp_port: args.RDPPortOption = 3390,
    xpra_port: args.XpraPortOption = 8888,
    metrics_port: args.MetricsPortOption = 9118,
    capella_arguments: capella_args.CapellaArguments = None,
    pv_license_server: pv_args.PureVariantsLicenseServerOption = "http://localhost:8080",
    pv_known_servers: pv_args.PureVariantsKnownServersOption = '[{"name": "test", "url": "http://example.localhost"}]',
    pv_lic_file_path: pv_args.PureVariantsLicenseFilePath = pathlib.Path(
        "./volumes/pure-variants/license.lic"
    ),
    t4c_license_configuration: capella_args.TeamForCapellaLicenseConfigurationOption = None,
    t4c_repository_list: capella_args.TeamForCapellaRepositoryListOption = None,
    _verbose: _logging.VerboseOption = False,
) -> None:
    helpers.print_cli_options(locals(), "running Capella")

    validators.validate_x_server_connection(
        remote=remote, connect_to_x_server=connect_to_x_server
    )
    validators.validate_rdp_password_option(connection_method, rdp_password)

    if not skip_build:
        capella_builder.capella(
            skip_base_image=False,
            skip_capella_image=False,
            cpu_architecture=cpu_architecture,
            image_prefix=image_prefix,
            image_tag=image_tag,
            uid=uid,
            push=push,
            no_cache=no_cache,
            capella_version=capella_version,
            remote=remote,
            t4c_client=t4c_client,
            build_type=build_type,
            capella_download_url=capella_download_url,
            capella_dropins=capella_dropins,
            pure_variants_client=pure_variants_client,
            pure_variants_version=pure_variants_version,
        )

    image = capella_builder.get_final_capella_tag(
        image_prefix=image_prefix,
        image_tag=image_tag,
        capella_version=capella_version,
        pure_variants_version=pure_variants_version,
        t4c_client=t4c_client,
        remote=remote,
        pure_variants_client=pure_variants_client,
    )

    environment: dict[str, str] = {}
    ports: dict[int, int] = {}
    volumes: dict[pathlib.Path, pathlib.PurePosixPath] = {}

    if disable_semantic_browser:
        environment["DISABLE_SEMANTIC_BROWSER_AUTO_REFRESH"] = "1"
    environment["LOG_LEVEL"] = log_level.value
    environment["MEMORY_MIN"] = memory_min
    environment["MEMORY_MAX"] = memory_max

    if workspace:
        volumes[workspace] = pathlib.PurePosixPath("/workspace")

    environment["AUTOSTART_CAPELLA"] = "1" if autostart_capella else "0"
    environment["RESTART_CAPELLA"] = "1" if restart_capella else "0"

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

    if t4c_license_configuration:
        environment["T4C_LICENCE_SECRET"] = t4c_license_configuration
    if t4c_repository_list:
        environment["T4C_JSON"] = t4c_repository_list

    docker.run_container(
        image_name=image,
        build_architecture=cpu_architecture,
        detach=detach,
        environment=environment,
        ports=ports,
        volumes=volumes,
        debug=debug,
        root=root,
        args=capella_arguments,
        after_run_callback=helpers.remote_callback_factory(
            remote=remote,
            connection_method=connection_method,
            rdp_port=rdp_port,
            xpra_port=xpra_port,
            xpra_subpath=xpra_subpath,
        ),
    )
