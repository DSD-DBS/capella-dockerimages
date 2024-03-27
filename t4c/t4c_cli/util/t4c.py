# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import datetime
import logging
import os
import pathlib

import yaml
from lxml import etree

from . import config, util

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
log = logging.getLogger("T4C")


def check_dir_for_aird_files(
    general_config: config.GeneralConfig, path: pathlib.Path
):
    aird_files = list(path.glob("*.aird"))

    entrypoint = general_config.git_config.entrypoint

    if not len(aird_files) == 1:
        raise RuntimeError(
            f"{general_config.error_prefix} - Entrypoint (if provided) or root directoy does not contain a .aird file"
        )

    if entrypoint and (
        not pathlib.Path(entrypoint).name == aird_files[0].name
    ):
        raise RuntimeError(
            f"{general_config.error_prefix} - .aird file found in git entrypoint directory does not match git entrypoint aird"
        )


def extract_t4c_commit_information(
    t4c_config: config.T4CConfig,
) -> tuple[str, datetime.datetime | None]:
    project_dir = pathlib.Path(t4c_config.project_dir_path)

    log.info("Start extracting t4c commit information in %s", project_dir)

    activity_metadata_file = util.get_single_file_by_t4c_pattern_or_raise(
        prefix="CommitHistory_",
        file_format="activitymetadata",
        root_dir=project_dir,
    )

    activitymetadata_tree: etree.ElementTree = etree.parse(
        project_dir / activity_metadata_file
    )

    activitymetadata: etree.Element = activitymetadata_tree.getroot()

    if activitymetadata is None:
        log.info(
            "activitymetadata root element was not found - commit history cannot be extracted"
        )
        return "", None

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
            commit_datetime = util.parse_t4c_commit_date(commit_date)
            if commit_datetime and commit_datetime > last_commit_datetime:
                last_commit_datetime = commit_datetime

        commit_information.append(activity_dict)

    log.info(
        "Finished extracting t4c commit information in %s",
        activity_metadata_file,
    )

    return (
        yaml.dump(commit_information, sort_keys=False),
        last_commit_datetime,
    )


def _create_activity_dict(
    activity: etree.Element,
) -> dict[str, str | None] | None:
    attributes = activity.attrib

    if commit_datetime := attributes.get("date", None):
        commit_datetime = util.parse_t4c_commit_date(attributes.get("date"))

    if description := attributes.get("description", None):
        description = description.rstrip()

        if "[Import][Application]" in description:
            return None

    return {
        "user": attributes.get("userId", None),
        "time": commit_datetime.isoformat() if commit_datetime else None,
        "description": description,
    }
