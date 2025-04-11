# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import glob
import logging
import os
import pathlib

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
log = logging.getLogger("T4C")


def check_dir_for_aird_files(resolved_model_dir: pathlib.Path) -> None:
    """Validate the project directory structure.

    Every Capella project should contain at least one .aird file.
    """

    if len(list(resolved_model_dir.glob("*.aird"))) == 0:
        raise RuntimeError(
            f"{resolved_model_dir.absolute()} contains no .aird file"
        )


def get_single_file_by_t4c_pattern_or_raise(
    prefix: str, file_format: str, root_dir: pathlib.Path
) -> str:
    pattern = (
        f"{glob.escape(prefix)}_????????_??????.{glob.escape(file_format)}"
    )

    matching_files = glob.glob(pattern, root_dir=root_dir)

    if not matching_files:
        raise FileNotFoundError(f"No files found matching pattern: {pattern}")

    if len(matching_files) > 1:
        raise FileExistsError(
            f"Multiple files found matching pattern: {pattern} - {matching_files}"
        )

    return matching_files[0]
