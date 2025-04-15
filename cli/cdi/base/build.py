# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import typer

from cdi import args, docker, git, helpers
from cdi import logging as _logging

from . import args as base_args

app = typer.Typer()


@app.command(
    name="base",
    help="Build the Base Image, which is used as a base for all other images.",
)
def command(
    *,
    cpu_architecture: args.CPUArchitectureOption,
    image_prefix: args.ImagePrefixOption = "",
    image_tag: args.ImageTagOption = "{cdi_revision}",
    push: args.PushOption = False,
    uid: base_args.UIDOption = base_args.UID_OPTION_DEFAULT,
    no_cache: args.NoCacheOption = False,
    labels: args.ImageLabelOption = None,
    _verbose: _logging.VerboseOption = False,
    suppress_cli_options: bool = False,
) -> None:
    if not suppress_cli_options:
        helpers.print_cli_options(locals(), "building base")
    docker.check_prerequisites()

    image_tag = image_tag.format(cdi_revision=git.get_current_cdi_revision())

    image_name = docker.build_image_name(image_prefix, "base", image_tag)

    docker.build_image(
        image_name=image_name,
        build_context="base",
        build_architecture=cpu_architecture,
        no_cache=no_cache,
        build_args={"UID": uid},
        labels=helpers.transform_labels(labels),
    )

    if push:
        docker.push_image(image_name)
