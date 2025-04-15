# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0
"""Prepare models in the $MODEL_INBOX_DIRECTORIES for Capella."""

import enum
import json
import logging
import os
import pathlib
import re
import string
import typing as t

from lxml import etree
from lxml.builder import E

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
log = logging.getLogger(__file__)


class _ProjectNature(enum.Enum):
    LIBRARY = "org.polarsys.capella.library.nature"
    PROJECT = "org.polarsys.capella.project.nature"


class _ProjectDict(t.TypedDict):
    name: t.NotRequired[str]
    revision: str
    nature: t.NotRequired[str]
    etree: t.NotRequired[etree._Element]  # etree of the .project file
    path: str  # Directory the repository has been cloned into
    entrypoint: (
        str | pathlib.Path
    )  # Entrypoint relative from the root of the repository

    location: t.NotRequired[pathlib.Path]  # Location resolved from path + entrypoint


def fetch_projects_from_environment() -> list[_ProjectDict]:
    return json.loads(os.getenv("ECLIPSE_PROJECTS_TO_LOAD", "[]"))


def resolve_entrypoint(project: _ProjectDict) -> None:
    if entrypoint := project["entrypoint"]:
        project["entrypoint"] = pathlib.Path(
            project["location"],
            str(pathlib.Path(entrypoint)).lstrip("/"),
        )

        assert isinstance(project["entrypoint"], pathlib.Path)
        project["location"] = project["entrypoint"].parent


def check_that_location_exists(project: _ProjectDict) -> None:
    if not project["location"].exists():
        raise FileNotFoundError(
            f"Couldn't find project location '{project['location']}'"
        )

    log.debug(
        "Found the following files in directory '%s': %s",
        project["location"],
        ", ".join([str(path) for path in project["location"].glob("*")]),
    )


def derive_project_name_from_aird(project_location: pathlib.Path) -> str:
    return next(project_location.glob("*.aird")).stem


def load_or_generate_project_etree(project: _ProjectDict) -> None:
    project_description_file: pathlib.Path = project["location"] / ".project"
    if project_description_file.exists():
        project["etree"] = etree.fromstring(project_description_file.read_bytes())
    else:
        project["etree"] = generate_project_etree(project)


def derive_project_name(project: _ProjectDict) -> None:
    name_element = project["etree"].find("name")
    if name_element is None or name_element.text is None:
        raise RuntimeError("Couldn't find project name in .project file.")
    project["name"] = name_element.text.strip()


def generate_project_etree(project: _ProjectDict) -> etree._Element:
    # More information:
    # https://help.eclipse.org/latest/index.jsp?topic=%2Forg.eclipse.platform.doc.isv%2Freference%2Fmisc%2Fproject_description_file.html&cp%3D2_1_3_11

    if project.get("nature", "").upper() in _ProjectNature.__members__:
        assert isinstance(project["nature"], str)
        nature = _ProjectNature[project["nature"]]
    else:
        nature = _ProjectNature.PROJECT

    return E.projectDescription(
        E.name(derive_project_name_from_aird(project["location"])),
        E.comment(),
        E.projects(),
        E.buildSpec(),
        E.natures(E.nature(nature.value)),
    )


def write_updated_project_file(project: _ProjectDict) -> None:
    project_description_file: pathlib.Path = project["location"] / ".project"
    project_description_file.write_bytes(etree.tostring(project["etree"]))


def resolve_duplicate_names(projects: list[_ProjectDict]) -> None:
    duplicated_projects_grouped = group_projects_by_name(projects)

    for duplicated_projects in duplicated_projects_grouped:
        for duplicated_project in duplicated_projects:
            append_revision_to_project_name(duplicated_project)

    # Check again for duplicated projects (same project name and same revision)
    duplicated_projects_grouped = group_projects_by_name(projects)
    for duplicated_projects in duplicated_projects_grouped:
        for counter, duplicated_project in enumerate(duplicated_projects):
            add_suffix_to_project_name(duplicated_project, str(counter))


def group_projects_by_name(
    projects: list[_ProjectDict],
) -> list[list[_ProjectDict]]:
    grouped_projects: dict[str, list[_ProjectDict]] = {}

    for project in projects:
        project_name = project["name"]
        if project_name in grouped_projects:
            grouped_projects[project_name].append(project)
        else:
            grouped_projects[project_name] = [project]

    return [
        projects_per_name
        for projects_per_name in grouped_projects.values()
        if len(projects_per_name) > 1
    ]


def add_suffix_to_project_name(project: _ProjectDict, suffix: str) -> None:
    new_name = project["name"] + "-" + suffix
    project["name"] = new_name

    element = project["etree"].find("name")
    if element is None:
        raise RuntimeError("Couldn't find project name in .project file.")
    element.text = new_name


def append_revision_to_project_name(project: _ProjectDict) -> None:
    valid_chars = string.ascii_letters + string.digits + "._-"
    sanitized_revision = re.sub(f"[^{valid_chars}]", "-", project["revision"])

    add_suffix_to_project_name(project, sanitized_revision)


def provide_project_dirs_to_capella_plugin(
    projects: list[_ProjectDict],
) -> None:
    locations = ":".join([str(project["location"]) for project in projects])
    with open("/etc/environment", "a", encoding="utf-8") as f:
        f.write(f"export MODEL_INBOX_DIRECTORIES={locations}\n")
    log.info("Set environment variable MODEL_INBOX_DIRECTORIES to '%s'", locations)


def main() -> None:
    projects = fetch_projects_from_environment()
    log.info("Found the following models: %s", projects)
    for project in projects:
        project["location"] = pathlib.Path(project["path"])
        resolve_entrypoint(project)
        check_that_location_exists(project)
        load_or_generate_project_etree(project)
        derive_project_name(project)

    resolve_duplicate_names(projects)

    for project in projects:
        write_updated_project_file(project)

    provide_project_dirs_to_capella_plugin(projects)


if __name__ == "__main__":
    main()
