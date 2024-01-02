# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0
"""EASE script to prepare the workspace for read-only containers.

.. note:
    The script can be invoked with
    ``/opt/capella/capella --launcher.suppressErrors -consolelog -application org.eclipse.ease.runScript -script "file:/opt/scripts/load_models.py"``

.. seealso:

    The acronym EASE stands for "Eclipse Advanced Scripting Environment".
    Further information: https://www.eclipse.org/ease/
"""
import enum
import json
import logging
import os
import pathlib
import re
import string
import subprocess
import tempfile
import typing as t

from eclipse.system.resources import importProject
from lxml import etree
from lxml.builder import E

logging.basicConfig(level="DEBUG")
log = logging.getLogger(__file__)

WORKSPACE_DIR = os.getenv("WORKSPACE_DIR", "/workspace")


class _ProjectNature(enum.Enum):
    library = "org.polarsys.capella.library.nature"
    project = "org.polarsys.capella.project.nature"


class _ProjectDict(t.TypedDict):
    name: t.NotRequired[str]
    url: str
    revision: str
    depth: int
    entrypoint: str | pathlib.Path
    username: str | None
    password: str | None
    nature: t.NotRequired[_ProjectNature | str]
    location: t.NotRequired[pathlib.Path]
    etree: t.NotRequired[etree.ElementTree]


def disable_welcome_screen() -> None:
    prefs = "\n".join(["eclipse.preferences.version=1", "showIntro=false"])
    prefs_path = pathlib.Path(
        f"{WORKSPACE_DIR}/.metadata/.plugins/org.eclipse.core.runtime/.settings/org.eclipse.ui.prefs"
    )
    prefs_path.parent.mkdir(parents=True, exist_ok=True)
    prefs_path.write_text(prefs, encoding="utf-8")
    log.info("Disabled Welcome screen")


def fetch_projects_from_environment() -> list[_ProjectDict]:
    projects: list[_ProjectDict] = []

    git_repo_url = os.getenv("GIT_URL")
    git_repo_revision = os.getenv("GIT_REVISION")

    if git_repo_url and git_repo_revision:
        projects.append(
            {
                "url": git_repo_url,
                "revision": git_repo_revision,
                "depth": int(os.getenv("GIT_DEPTH", "0")),
                "entrypoint": os.environ["GIT_ENTRYPOINT"],
                "username": os.getenv("GIT_USERNAME", None),
                "password": os.getenv("GIT_PASSWORD", None),
            }
        )

    return projects + json.loads(os.getenv("GIT_REPOS_JSON", "[]"))


def clone_git_model(project: _ProjectDict) -> None:
    log.info("Cloning git repository with url %s", project["url"])

    project["location"] = pathlib.Path(tempfile.mkdtemp(prefix="model_"))

    flags = []

    if revision := project["revision"]:
        flags += ["--single-branch", "--branch", revision]

    git_depth = project["depth"]
    if git_depth != 0:
        flags += ["--depth", str(git_depth)]

    subprocess.run(
        ["git", "clone", project["url"], str(project["location"])] + flags,
        check=True,
        env={
            "GIT_USERNAME": project.get("username", None) or "",
            "GIT_PASSWORD": project.get("password", None) or "",
            "GIT_ASKPASS": os.environ["GIT_ASKPASS"],
        },
    )
    log.info(
        "Clone of git repository with url %s was successful", project["url"]
    )


def resolve_entrypoint(project: _ProjectDict) -> None:
    if entrypoint := project["entrypoint"]:
        project["entrypoint"] = pathlib.Path(
            project["location"],
            str(pathlib.Path(entrypoint)).lstrip("/"),
        )

        assert isinstance(project["entrypoint"], pathlib.Path)
        project["location"] = project["entrypoint"].parent


def derive_project_name_from_aird(project_location: pathlib.Path) -> str:
    return next(project_location.glob("*.aird")).stem


def load_or_generate_project_etree(project: _ProjectDict) -> None:
    project_description_file: pathlib.Path = project["location"] / ".project"
    if project_description_file.exists():
        project["etree"] = etree.fromstring(
            project_description_file.read_bytes()
        )
    else:
        project["etree"] = generate_project_etree(project)


def derive_project_name(project: _ProjectDict) -> None:
    project["name"] = project["etree"].find("name").text.strip()


def generate_project_etree(project: _ProjectDict) -> etree.ElementTree:
    # More information:
    # https://help.eclipse.org/latest/index.jsp?topic=%2Forg.eclipse.platform.doc.isv%2Freference%2Fmisc%2Fproject_description_file.html&cp%3D2_1_3_11

    if project.get("nature", "") in _ProjectNature.__members__:
        assert isinstance(project["nature"], str)
        nature = _ProjectNature[project["nature"]]
    else:
        nature = _ProjectNature.project

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


def import_project(project: _ProjectDict) -> None:
    log.info("Loading project into workspace: %s", str(project["location"]))
    importProject(str(project["location"]))
    log.info("Loading of project was successful: %s", str(project["location"]))


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

    project["etree"].find("name").text = new_name


def append_revision_to_project_name(project: _ProjectDict) -> None:
    valid_chars = string.ascii_letters + string.digits + "._-"
    sanitized_revision = re.sub(f"[^{valid_chars}]", "-", project["revision"])

    add_suffix_to_project_name(project, sanitized_revision)


def main():
    projects = fetch_projects_from_environment()
    print("---START_LOAD_MODEL---")
    try:
        for project in projects:
            clone_git_model(project)
            resolve_entrypoint(project)
            load_or_generate_project_etree(project)
            derive_project_name(project)

        resolve_duplicate_names(projects)

        for project in projects:
            write_updated_project_file(project)
            import_project(project)
        print("---FINISH_LOAD_MODEL---")
    except Exception as e:
        print("---FAILURE_LOAD_MODEL---")
        raise e
    disable_welcome_screen()


if __name__ == "__main__":
    main()
