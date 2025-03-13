# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import logging
import typing as t

import typer

from cdi import _repository_root, args, docker, formatting, git, helpers
from cdi import logging as _logging
from cdi.base import args as base_args
from cdi.base import build as base_build
from cdi.pure_variants import args as pv_args
from cdi.pure_variants import build as pv_build

log = logging.getLogger(__name__)

app = typer.Typer()


ECLIPSE_OPTIONS = "Eclipse Options"

SkipEclipseImageOption = t.Annotated[
    bool,
    typer.Option(
        "--skip-eclipse-image",
        help=(
            "Skip the build of the Eclipse image."
            " Use this option if you already have a pre-built Eclipse image"
            " that you want to extend."
        ),
    ),
]

EclipseVersionOption = t.Annotated[
    str,
    typer.Option(
        help="Version of the Eclipse client to install",
        envvar="ECLIPSE_VERSION",
        rich_help_panel=ECLIPSE_OPTIONS,
    ),
]


def validate_eclipse_archive(
    eclipse_version: str,
    build_architecture: args.CPUArchitectureOption,
) -> None:
    """Validate that the Eclipse archive must be present."""
    eclipse_directory = (
        _repository_root
        / "eclipse"
        / "versions"
        / eclipse_version
        / build_architecture.value
    )

    if not (eclipse_directory / "eclipse.tar.gz").is_file():
        log.error(
            "The 'eclipse.tar.gz' archive was not found."
            " Please download it from the product from the %s"
            " and place it in the 'eclipse/versions/%s/%s' directory."
            " More information is available in our %s.",
            formatting.build_rich_link(
                link="https://download.eclipse.org/eclipse/downloads/",
                text="Eclipse website",
            ),
            eclipse_version,
            build_architecture.value,
            formatting.build_rich_link(
                link="https://dsd-dbs.github.io/capella-dockerimages/eclipse/base/#download-eclipse",
                text="documentation",
            ),
        )
        raise typer.Exit(1)


@app.command(
    name="eclipse",
    help="Build the Eclipse Image, including pure::variants or remote support.",
)
def eclipse(
    *,
    skip_base_image: base_args.SkipBaseImageOption = False,
    skip_eclipse_image: SkipEclipseImageOption = False,
    cpu_architecture: args.CPUArchitectureOption,
    image_prefix: args.ImagePrefixOption = "",
    image_tag: args.ImageTagOption = "{eclipse_version}-{cdi_revision}",
    base_image_tag: base_args.BaseImageTagOption = "{cdi_revision}",
    uid: base_args.UIDOption = base_args.UID_OPTION_DEFAULT,
    push: args.PushOption = False,
    no_cache: args.NoCacheOption = False,
    eclipse_version: EclipseVersionOption = "4.27",
    remote: args.RemoteOption = True,
    pure_variants_client: pv_args.PureVariantsOption = False,
    pure_variants_version: pv_args.PureVariantsVersionOption = "6.0.1",
    labels: args.ImageLabelOption = None,
    _verbose: _logging.VerboseOption = False,
) -> None:
    helpers.print_cli_options(locals(), "building Eclipse")

    if skip_eclipse_image and not remote and not pure_variants_client:
        log.error(
            "You must enable at least one of the options `--remote` or `--pv-client` if you want to skip the Eclipse image."
        )
        raise typer.Exit(1)

    validate_eclipse_archive(eclipse_version, cpu_architecture)
    base_image_tag = base_image_tag.format(
        cdi_revision=git.get_current_cdi_revision()
    )

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

    image_tag = image_tag.format(
        eclipse_version=eclipse_version,
        pure_variants_version=pure_variants_version,
        cdi_revision=git.get_current_cdi_revision(),
    )

    image_core = "eclipse"
    image_name = docker.build_image_name(
        image_prefix, image_core + "/base", image_tag
    )
    base_image_name = docker.build_image_name(
        image_prefix, "base", base_image_tag
    )

    if not skip_eclipse_image:
        with docker.build_dockerignore(
            "eclipse", ["versions/*", f"!versions/{eclipse_version}"]
        ):
            docker.build_image(
                image_name=image_name,
                build_context="eclipse",
                build_architecture=cpu_architecture,
                no_cache=no_cache,
                build_args={
                    "BUILD_ARCHITECTURE": cpu_architecture.value,
                    "BASE_IMAGE": base_image_name,
                    "ECLIPSE_VERSION": eclipse_version,
                },
                labels=helpers.transform_labels(labels),
            )

    if remote:
        image_core += "/remote"
        remote_image_name = docker.build_image_name(
            image_prefix, image_core, image_tag
        )
        docker.build_image(
            image_name=remote_image_name,
            build_context="remote",
            build_architecture=cpu_architecture,
            no_cache=no_cache,
            build_args={"BASE_IMAGE": image_name},
            labels=helpers.transform_labels(labels),
        )
        image_name = remote_image_name

    if pure_variants_client:
        pure_variants_image = docker.build_image_name(
            image_prefix, image_core + "/pure-variants", image_tag
        )
        pv_build.build_pure_variants_image(
            pure_variants_version=pure_variants_version,
            image_name=pure_variants_image,
            base_image_name=image_name,
            build_architecture=cpu_architecture,
            no_cache=no_cache,
            labels=helpers.transform_labels(labels),
        )
        image_name = pure_variants_image

    if push:
        docker.push_image(image_name)


def get_final_eclipse_image_tag(
    *,
    image_prefix: str,
    image_tag: str,
    eclipse_version: str,
    pure_variants_version: str,
    remote: bool,
    pure_variants_client: bool,
) -> str:
    image_tag = image_tag.format(
        eclipse_version=eclipse_version,
        pure_variants_version=pure_variants_version,
        cdi_revision=git.get_current_cdi_revision(),
    )

    image = "eclipse"
    if remote:
        image += "/remote"
    if pure_variants_client:
        image += "/pure-variants"

    if image == "eclipse":
        # For backwards compatibility, keep the old "eclipse/base" image name
        image = "eclipse/base"

    return docker.build_image_name(image_prefix, image, image_tag)
