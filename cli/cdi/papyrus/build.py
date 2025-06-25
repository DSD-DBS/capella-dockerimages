# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import logging

import typer

from cdi import (
    _repository_root,
    args,
    docker,
    formatting,
    git,
    helpers,
    validators,
)
from cdi import logging as _logging
from cdi.base import args as base_args
from cdi.base import build as base_build

from . import args as papyrus_args

log = logging.getLogger(__name__)

app: typer.Typer = typer.Typer()


def validate_papyrus_archive(
    papyrus_version: str,
) -> None:
    """Validate that the Papyrus archive must be present."""
    papyrus_directory = (
        _repository_root / "papyrus" / "versions" / papyrus_version
    )
    if not (papyrus_directory / "papyrus.tar.gz").is_file():
        log.error(
            "The 'papyrus.tar.gz' archive was not found."
            " Please download it from the product from the %s"
            " and place it in the 'papyrus/versions/%s' directory."
            " More information is available in our %s.",
            formatting.build_rich_link(
                link="https://eclipse.dev/papyrus/download.html",
                text="Papyrus website",
            ),
            papyrus_version,
            formatting.build_rich_link(
                link="https://dsd-dbs.github.io/capella-dockerimages/papyrus/base/#download-papyrus",
                text="documentation",
            ),
        )
        raise typer.Exit(1)


@app.command(
    name="papyrus",
    help="Build the Papyrus Image.",
)
def papyrus(
    *,
    skip_base_image: base_args.SkipBaseImageOption = False,
    skip_papyrus_image: papyrus_args.SkipPapyrusImageOption = False,
    image_prefix: args.ImagePrefixOption = "",
    image_tag: args.ImageTagOption = "{papyrus_version}-{cdi_revision}",
    base_image_tag: base_args.BaseImageTagOption = "{cdi_revision}",
    uid: base_args.UIDOption = base_args.UID_OPTION_DEFAULT,
    push: args.PushOption = False,
    no_cache: args.NoCacheOption = False,
    papyrus_version: papyrus_args.PapyrusVersionOption = "6.4.0",
    remote: args.RemoteOption = True,
    labels: args.ImageLabelOption = None,
    _verbose: _logging.VerboseOption = False,
) -> None:
    helpers.print_cli_options(locals(), "building Papyrus")
    if skip_papyrus_image and not remote:
        log.error(
            "You must enable `--remote` if you want to skip the Papyrus image."
        )
        raise typer.Exit(1)

    validators.validate_build_architecture(docker.SupportedArchitecture.amd64)
    validate_papyrus_archive(papyrus_version=papyrus_version)
    base_image_tag = base_image_tag.format(
        cdi_revision=git.get_current_cdi_revision()
    )

    if not skip_base_image:
        base_build.command(
            cpu_architecture=docker.SupportedArchitecture.amd64,
            image_prefix=image_prefix,
            image_tag=base_image_tag,
            uid=uid,
            push=False,
            no_cache=no_cache,
            suppress_cli_options=True,
        )

    image_tag = image_tag.format(
        papyrus_version=papyrus_version,
        cdi_revision=git.get_current_cdi_revision(),
    )
    image_name = docker.build_image_name(
        image_prefix, "papyrus/base", image_tag
    )
    base_image_name = docker.build_image_name(
        image_prefix, "base", base_image_tag
    )

    helpers.copy_memory_flags_file(
        _repository_root / "papyrus" / "set_memory_flags.py"
    )
    with docker.build_dockerignore(
        "papyrus", ["versions/*", f"!versions/{papyrus_version}"]
    ):
        docker.build_image(
            image_name=image_name,
            build_context="papyrus",
            build_architecture=docker.SupportedArchitecture.amd64,
            no_cache=no_cache,
            build_args={
                "BASE_IMAGE": base_image_name,
                "PAPYRUS_VERSION": papyrus_version,
            },
            labels=helpers.transform_labels(labels),
        )

    if push:
        docker.push_image(image_name)

    if remote:
        remote_image_name = docker.build_image_name(
            image_prefix, "papyrus/remote", image_tag
        )
        docker.build_image(
            image_name=remote_image_name,
            build_context="remote",
            build_architecture=docker.SupportedArchitecture.amd64,
            no_cache=no_cache,
            build_args={"BASE_IMAGE": image_name},
            labels=helpers.transform_labels(labels),
        )
        image_name = remote_image_name

        if push:
            docker.push_image(image_name)
