# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pathlib


def inject_pure_variants(
    environment: dict[str, str],
    volumes: dict[pathlib.Path, pathlib.PurePosixPath],
    *,
    pv_client: bool,
    pv_license_server: str,
    pv_known_servers: str,
    pv_lic_file_path: pathlib.Path,
) -> None:
    if not pv_client:
        return

    environment["PURE_VARIANTS_LICENSE_SERVER"] = pv_license_server
    environment["PURE_VARIANTS_KNOWN_SERVERS"] = pv_known_servers
    volumes[pv_lic_file_path] = pathlib.PurePosixPath(
        "/inputs/pure-variants/license.lic"
    )
