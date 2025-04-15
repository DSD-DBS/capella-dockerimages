# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import typer

from cdi import args, docker, git, helpers
from cdi import logging as _logging
from cdi.base import args as base_args
from cdi.base import build as base_build

from . import args as jupyter_args

app: typer.Typer = typer.Typer()


@app.command(
    name="jupyter",
    help="Build the Jupyter Image.",
)
def jupyter(
    *,
    skip_base_image: base_args.SkipBaseImageOption = False,
    cpu_architecture: args.CPUArchitectureOption,
    image_prefix: args.ImagePrefixOption = "",
    image_tag: args.ImageTagOption = jupyter_args.IMAGE_TAG_DEFAULT,
    base_image_tag: base_args.BaseImageTagOption = "{cdi_revision}",
    uid: base_args.UIDOption = base_args.UID_OPTION_DEFAULT,
    push: args.PushOption = False,
    no_cache: args.NoCacheOption = False,
    labels: args.ImageLabelOption = None,
    _verbose: _logging.VerboseOption = False,
) -> None:
    helpers.print_cli_options(locals(), "building Jupyter")
    base_image_tag = base_image_tag.format(
        cdi_revision=git.get_current_cdi_revision()
    )
    image_tag = image_tag.format(cdi_revision=git.get_current_cdi_revision())

    if not skip_base_image:
        base_build.command(
            cpu_architecture=cpu_architecture,
            image_prefix=image_prefix,
            image_tag=base_image_tag,
            uid=uid,
            push=False,
            no_cache=no_cache,
            suppress_cli_options=True,
            labels=labels,
        )

    image_name = docker.build_image_name(
        image_prefix, "jupyter-notebook", image_tag
    )
    base_image_name = docker.build_image_name(
        image_prefix, "base", base_image_tag
    )

    docker.build_image(
        image_name=image_name,
        build_context="jupyter",
        build_architecture=cpu_architecture,
        no_cache=no_cache,
        build_args={
            "BASE_IMAGE": base_image_name,
        },
        labels=helpers.transform_labels(labels),
    )

    if push:
        docker.push_image(image_name)
