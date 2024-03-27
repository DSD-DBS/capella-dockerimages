# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import datetime
import glob
import logging
import os
import pathlib
import re

from . import config

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
log = logging.getLogger("Git")


def is_capella_5_x_x(t4c_config: config.T4CConfig) -> bool:
    return bool(re.match(r"5.[0-9]+.[0-9]+", t4c_config.capella_version))


def is_capella_5_0_x(t4c_config: config.T4CConfig) -> bool:
    return bool(re.match(r"5.0.[0-9]+", t4c_config.capella_version))


def format_datetime_to_t4c_format(datetime_arg: datetime.datetime) -> str:
    return datetime_arg.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]


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


def parse_t4c_commit_date(date_str: str) -> datetime.datetime | None:
    try:
        return datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f%z")
    except ValueError:
        log.error("Failed to parse date: %s", date_str)
        return None


def determine_model_dir(
    root_path: pathlib.Path,
    entrypoint: str | None,
    create_if_not_exist: bool = False,
):
    model_dir = root_path
    if entrypoint:
        model_dir = pathlib.Path(
            root_path, str(pathlib.Path(entrypoint).parent).lstrip("/")
        )

    if create_if_not_exist:
        model_dir.mkdir(exist_ok=True, parents=True)

    return model_dir
