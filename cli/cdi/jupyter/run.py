# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import logging
import pathlib

import typer

from cdi import args, docker, git, helpers
from cdi import logging as _logging
from cdi.base import args as base_args
from cdi.jupyter import build as jupyter_builder

from . import args as jupyter_args

log = logging.getLogger(__name__)

app = typer.Typer()


@app.command(
    name="jupyter",
    help="Run JupyterLab in a container.",
)
def jupyter(
    *,
    detach: args.RunDetachedOption = False,
    root: args.RunAsRootOption = False,
    debug: args.DebugOption = False,
    skip_build: args.SkipBuildOption = False,
    cpu_architecture: args.CPUArchitectureOption,
    image_prefix: args.ImagePrefixOption = "",
    image_tag: args.ImageTagOption = jupyter_args.IMAGE_TAG_DEFAULT,
    uid: base_args.UIDOption = base_args.UID_OPTION_DEFAULT,
    push: args.PushOption = False,
    no_cache: args.NoCacheOption = False,
    workspace: args.WorkspacePathOption = None,
    jupyter_base_url: jupyter_args.JupyterBaseURLOption = "/jupyter",
    jupyter_port: jupyter_args.JupyterPortOption = 8888,
    metrics_port: args.MetricsPortOption = 9118,
    _verbose: _logging.VerboseOption = False,
) -> None:
    helpers.print_cli_options(locals(), "running Jupyter")
    image_tag = image_tag.format(cdi_revision=git.get_current_cdi_revision())

    if not skip_build:
        jupyter_builder.jupyter(
            skip_base_image=False,
            cpu_architecture=cpu_architecture,
            image_prefix=image_prefix,
            image_tag=image_tag,
            uid=uid,
            push=push,
            no_cache=no_cache,
        )

    environment: dict[str, str] = {}
    ports: dict[int, int] = {}
    volumes: dict[pathlib.Path, pathlib.PurePosixPath] = {}

    if workspace:
        volumes[workspace] = pathlib.PurePosixPath("/workspace")
        environment["WORKSPACE_DIR"] = str(workspace)

    ports[metrics_port] = 9118
    ports[jupyter_port] = 8888

    environment["JUPYTER_BASE_URL"] = jupyter_base_url

    def jupyter_callback() -> None:
        log.info(
            "To connect to the container, connect to http://localhost:%s%s in a browser.",
            jupyter_port,
            jupyter_base_url,
        )

    docker.run_container(
        image_name=docker.build_image_name(
            image_prefix, "jupyter-notebook", image_tag
        ),
        build_architecture=cpu_architecture,
        detach=detach,
        environment=environment,
        ports=ports,
        volumes=volumes,
        debug=debug,
        root=root,
        after_run_callback=jupyter_callback,
    )
