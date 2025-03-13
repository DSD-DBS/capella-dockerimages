# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from cdi import docker


def build_pure_variants_image(
    *,
    pure_variants_version: str,
    image_name: str,
    base_image_name: str,
    build_architecture: docker.SupportedArchitecture,
    no_cache: bool,
    labels: list[tuple[str, str]] | None,
) -> None:
    docker.build_image(
        image_name=image_name,
        build_context="pure-variants",
        build_architecture=build_architecture,
        no_cache=no_cache,
        build_args={
            "BASE_IMAGE": base_image_name,
            "PURE_VARIANTS_VERSION": pure_variants_version,
        },
        labels=labels,
    )
