# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import datetime
import glob
import logging
import os
import pathlib

import yaml
from lxml import etree

from . import config

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
log = logging.getLogger("T4C")


def check_dir_for_aird_files(path: pathlib.Path) -> None:
    aird_files = list(path.glob("*.aird"))

    entrypoint = config.config.git.entrypoint

    if not len(aird_files) == 1:
        raise RuntimeError(
            "Entrypoint (if provided) or root directoy does not contain a .aird file"
        )

    if entrypoint:
        entrypoint_filename = pathlib.Path(entrypoint).name
        found_filename = aird_files[0].name
        if entrypoint_filename and (not entrypoint_filename == found_filename):
            raise RuntimeError(
                f"Found {found_filename}, but expected {entrypoint_filename} as provided."
            )


def extract_t4c_commit_information() -> tuple[str, datetime.datetime | None]:
    project_dir = pathlib.Path(config.config.t4c.project_dir_path)

    log.info(
        "Start extracting TeamForCapella commit information in %s", project_dir
    )

    activity_metadata_file = get_single_file_by_t4c_pattern_or_raise(
        prefix="CommitHistory_",
        file_format="activitymetadata",
        root_dir=project_dir,
    )

    activitymetadata_tree: etree._ElementTree = etree.parse(
        project_dir / activity_metadata_file
    )

    activitymetadata: etree._Element = activitymetadata_tree.getroot()

    if len(activitymetadata) == 0:
        log.info("no commits since last backup")
        return "", None

    commit_information: list[dict[str, str | None]] = []
    last_commit_datetime = datetime.datetime.fromtimestamp(0, tz=datetime.UTC)

    for activity in activitymetadata:
        activity_dict = _create_activity_dict(activity)

        if not activity_dict:
            continue

        if commit_date := activity.attrib.get("date", None):
            commit_datetime = datetime.datetime.fromisoformat(commit_date)
            if commit_datetime and commit_datetime > last_commit_datetime:
                last_commit_datetime = commit_datetime

        commit_information.append(activity_dict)

    log.info(
        "Finished extracting TeamForCapella commit information in %s",
        activity_metadata_file,
    )

    return (
        yaml.dump(commit_information, sort_keys=False),
        last_commit_datetime,
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


def _create_activity_dict(
    activity: etree._Element,
) -> dict[str, str | None] | None:
    attributes = activity.attrib

    if description := attributes.get("description", None):
        description = description.rstrip()

        if "[Import][Application]" in description:
            return None

    return {
        "user": attributes.get("userId", None),
        "time": attributes.get("date", None),
        "description": description,
    }
