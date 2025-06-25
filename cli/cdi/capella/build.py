# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import logging

import typer
import yaml

from cdi import _repository_root, args, docker, formatting, git, helpers
from cdi import logging as _logging
from cdi.base import args as base_args
from cdi.base import build as base_builder
from cdi.capella import args as capella_args
from cdi.pure_variants import args as pv_args
from cdi.pure_variants import build as pv_builder

log = logging.getLogger(__name__)

app = typer.Typer()


def load_dropins_files(
    capella_version: str,
) -> dict[str, list[str]]:
    """Load the dropins files from the Capella version directory."""

    base_dir = _repository_root / "capella" / "versions" / capella_version
    dropins = yaml.safe_load(
        (base_dir / "dropins.yml").read_text(encoding="utf-8")
    )["dropins"]

    dropins_overwrites = {}
    dropins_overwrites_path = base_dir / "dropins.overwrites.yml"
    if dropins_overwrites_path.exists():
        dropins_overwrites_content = yaml.safe_load(
            dropins_overwrites_path.read_text(encoding="utf-8")
        )
        if "dropins" in dropins_overwrites_content:
            dropins_overwrites = dropins_overwrites_content["dropins"]

    return dropins | dropins_overwrites


def validate_dropins(
    capella_version: str,
    dropins: list[str],
) -> None:
    """Make sure that the list of dropins is available for the Capella version."""
    available_dropins = load_dropins_files(capella_version)

    for dropin in dropins:
        if dropin and dropin not in available_dropins:
            log.error(
                "Dropin '%s' not found in the list of supported dropins for Capella version %s."
                " There are multiple options to resolve the issue:\n"
                "1. If the dropin is missing in the %s"
                " and you think it should be there, please open a new %s\n"
                "2. Download the dropins and add them to the 'capella/versions/%s/dropins' directory.\n"
                "3. Create a file 'capella/versions/%s/dropins.overwrites.yml' and add the required dropins.",
                dropin,
                capella_version,
                formatting.build_rich_link(
                    link="https://github.com/DSD-DBS/capella-dockerimages/blob/main/capella/versions/7.0.0/dropins.yml",
                    text="list of dropins",
                ),
                formatting.build_rich_link(
                    link="https://github.com/DSD-DBS/capella-dockerimages/issues",
                    text="GitHub issue",
                ),
                capella_version,
                capella_version,
            )
            raise typer.Exit(1)


def validate_capella_archive(
    build_type: capella_args.BuildTypeOption,
    build_architecture: args.CPUArchitectureOption,
    capella_version: str,
) -> None:
    """When the offline build is used, the Capella archive must be present."""
    if build_type == capella_args.BuildType.OFFLINE:
        capella_directory = (
            _repository_root
            / "capella"
            / "versions"
            / capella_version
            / build_architecture.value
        )
        if (
            not (capella_directory / "capella.zip").is_file()
            and not (capella_directory / "capella.tar.gz").is_file()
        ):
            log.error(
                "Neither 'capella.tar.gz' nor 'capella.zip' found."
                " Please download it from the Linux product from the %s"
                " and place it in the 'capella/versions/%s/%s' directory."
                " More information in our %s."
                " Alternatively, use '--build-type online'.",
                formatting.build_rich_link(
                    link="https://mbse-capella.org/download.html",
                    text="Capella website",
                ),
                capella_version,
                build_architecture.value,
                formatting.build_rich_link(
                    link="https://dsd-dbs.github.io/capella-dockerimages/capella/base/#optional-download-capella-manually",
                    text="documentation",
                ),
            )
            raise typer.Exit(1)


def validate_t4c_archive(*, t4c_client: bool, capella_version: str) -> None:
    """When the t4c client should be installed, it must be present on the machine."""
    if t4c_client:
        t4c_directory = (
            _repository_root / "t4c" / "updateSite" / capella_version
        )
        if len(list(t4c_directory.glob("*.zip"))) != 1:
            log.error(
                "No or more than one T4C client archive found in the directory 't4c/updateSite/%s'."
                " More information how to download the TeamForCapella archive is available in our %s",
                capella_version,
                formatting.build_rich_link(
                    link="https://dsd-dbs.github.io/capella-dockerimages/capella/t4c/base/#download-teamforcapella-bundle",
                    text="documentation",
                ),
            )
            raise typer.Exit(1)


def validate_pv_archive(
    *, pv_client: bool, pure_variants_version: str
) -> None:
    """When the pure::variants client should be installed, it must be present on the machine."""
    if pv_client:
        pv_directory = (
            _repository_root
            / "pure-variants"
            / "versions"
            / pure_variants_version
        )
        if len(list(pv_directory.glob("*.zip"))) != 1:
            log.error(
                "No or more than one pure::variants archive found in the directory 'pure-variants/versions/%s'."
                " More information how to download the pure::variants archive is available in our %s.",
                pure_variants_version,
                formatting.build_rich_link(
                    link="https://dsd-dbs.github.io/capella-dockerimages/pure-variants/#download-the-purevariants-archive",
                    text="documentation",
                ),
            )
            raise typer.Exit(1)


@app.command(
    name="capella",
    help="Build the Capella Image, including TeamForCapella, pure::variants, or remote support.",
)
def capella(
    *,
    skip_base_image: base_args.SkipBaseImageOption = False,
    skip_capella_image: capella_args.SkipCapellaImageOption = False,
    cpu_architecture: args.CPUArchitectureOption,
    image_prefix: args.ImagePrefixOption = "",
    image_tag: args.ImageTagOption = "{capella_version}-{cdi_revision}",
    base_image_tag: base_args.BaseImageTagOption = "{cdi_revision}",
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
    labels: args.ImageLabelOption = None,
    _verbose: _logging.VerboseOption = False,
) -> None:
    helpers.print_cli_options(locals(), "building Capella")

    if (
        skip_capella_image
        and not remote
        and not t4c_client
        and not pure_variants_client
    ):
        log.error(
            "You must enable at least one of the options `--remote`, `--t4c-client`, or `--pv-client` if you want to skip the Capella image."
        )
        raise typer.Exit(1)

    if not skip_capella_image:
        validate_dropins(capella_version, dropins=capella_dropins.split(","))
        validate_capella_archive(build_type, cpu_architecture, capella_version)
    validate_t4c_archive(
        t4c_client=t4c_client, capella_version=capella_version
    )
    validate_pv_archive(
        pv_client=pure_variants_client,
        pure_variants_version=pure_variants_version,
    )

    base_image_tag = base_image_tag.format(
        cdi_revision=git.get_current_cdi_revision()
    )

    if not skip_base_image:
        base_builder.command(
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
        capella_version=capella_version,
        pure_variants_version=pure_variants_version,
        cdi_revision=git.get_current_cdi_revision(),
    )

    image_core = "capella"
    image_name = docker.build_image_name(
        image_prefix, image_core + "/base", image_tag
    )
    base_image_name = docker.build_image_name(
        image_prefix, "base", base_image_tag
    )

    if not skip_capella_image:
        helpers.copy_memory_flags_file(
            _repository_root / "capella" / "setup" / "set_memory_flags.py"
        )
        with docker.build_dockerignore(
            "capella", ["versions/*", f"!versions/{capella_version}"]
        ):
            docker.build_image(
                image_name=image_name,
                build_context="capella",
                build_architecture=cpu_architecture,
                no_cache=no_cache,
                build_args={
                    "BUILD_ARCHITECTURE": cpu_architecture.value,
                    "BASE_IMAGE": base_image_name,
                    "BUILD_TYPE": build_type.value,
                    "CAPELLA_DOWNLOAD_URL": capella_download_url or "",
                    "CAPELLA_VERSION": capella_version,
                    "CAPELLA_DROPINS": capella_dropins,
                },
                labels=helpers.transform_labels(labels),
            )
        if push:
            docker.push_image(image_name)

    if t4c_client:
        image_core = "t4c/client"
        t4c_image_name = docker.build_image_name(
            image_prefix, image_core + "/base", image_tag
        )
        with docker.build_dockerignore(
            "t4c", ["updateSite/*", f"!updateSite/{capella_version}"]
        ):
            docker.build_image(
                image_name=t4c_image_name,
                build_context="t4c",
                build_architecture=cpu_architecture,
                no_cache=no_cache,
                build_args={
                    "BASE_IMAGE": image_name,
                    "CAPELLA_VERSION": capella_version,
                },
                labels=helpers.transform_labels(labels),
            )
        image_name = t4c_image_name
        if push:
            docker.push_image(image_name)

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
        if push:
            docker.push_image(image_name)

    if pure_variants_client:
        pure_variants_image = docker.build_image_name(
            image_prefix, image_core + "/pure-variants", image_tag
        )
        pv_builder.build_pure_variants_image(
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

    if build_type == capella_args.BuildType.ONLINE:
        log.warning(
            "It's highly recommended to use `--build-type offline` if you build the image frequently,"
            " otherwise the Capella client will be downloaded each time!"
            "\nMore information in the %s.",
            formatting.build_rich_link(
                link="https://dsd-dbs.github.io/capella-dockerimages/capella/base/#optional-download-capella-manually",
                text="documentation",
            ),
        )


def get_final_capella_tag(
    *,
    image_prefix: str,
    image_tag: str,
    capella_version: str,
    pure_variants_version: str | None,
    t4c_client: bool,
    remote: bool,
    pure_variants_client: bool,
) -> str:
    image_tag = image_tag.format(
        capella_version=capella_version,
        pure_variants_version=pure_variants_version,
        cdi_revision=git.get_current_cdi_revision(),
    )

    image = "capella"
    if t4c_client:
        image = "t4c/client"
    image += "/remote" if remote else "/base"
    if pure_variants_client:
        image += "/pure-variants"

    return docker.build_image_name(image_prefix, image, image_tag)
