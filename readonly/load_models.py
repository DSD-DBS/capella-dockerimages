# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0
"""EASE script to prepare the workspace for read-only containers.

.. note:
    The script can be invoked with
    ``/opt/capella/capella --launcher.suppressErrors -consolelog -application org.eclipse.ease.runScript -script "file:/opt/scripts/load_models.py"``

.. seealso:

    The acronym EASE stands for "Eclipse Advanced Scripting Environment".
    Further information: https://www.eclipse.org/ease/
"""
import json
import logging
import os
import pathlib
import subprocess
import tempfile
import typing as t

from eclipse.system.resources import importProject
from lxml import etree as ET
from lxml.builder import E

logging.basicConfig(level="DEBUG")
log = logging.getLogger(__file__)


def disable_welcome_screen() -> None:
    prefs = "\n".join(["eclipse.preferences.version=1", "showIntro=false"])
    prefs_path = pathlib.Path(
        "/workspace/.metadata/.plugins/org.eclipse.core.runtime/.settings/org.eclipse.ui.prefs"
    )
    prefs_path.parent.mkdir(parents=True, exist_ok=True)
    prefs_path.write_text(prefs)
    log.info("Disabled Welcome screen")


def fetch_projects_from_environment() -> list[dict[str, str]]:
    projects = []

    git_repo_url = os.getenv("GIT_URL")
    git_repo_revision = os.getenv("GIT_REVISION")

    if git_repo_url and git_repo_revision:
        projects.append(
            {
                "url": git_repo_url,
                "revision": git_repo_revision,
                "depth": os.getenv("GIT_DEPTH"),
                "entrypoint": os.getenv("GIT_ENTRYPOINT"),
                "username": None,
                "password": None,
            }
        )

    return projects + json.loads(os.getenv("GIT_REPOS_JSON", "[]"))


def clone_git_model(project: dict[str, str]) -> None:
    log.info("Cloning git repository with url %s", project["url"])

    project["location"] = pathlib.Path(tempfile.mkdtemp(prefix="model_"))

    flags = []

    if revision := project["revision"]:
        flags += ["--single-branch", "--branch", revision]

    git_depth = int(project.get("depth", 0))
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


def resolve_entrypoint(project: dict[str, str]) -> None:
    if entrypoint := project["entrypoint"]:
        project["location"] = pathlib.Path(
            project["location"],
            str(pathlib.Path(entrypoint).parent).lstrip("/"),
        )


def generate_project_file(project: dict[str, str]) -> None:
    # More information:
    # https://help.eclipse.org/latest/index.jsp?topic=%2Forg.eclipse.platform.doc.isv%2Freference%2Fmisc%2Fproject_description_file.html&cp%3D2_1_3_11

    project_description_file: pathlib.Path = project["location"] / ".project"
    if not project_description_file.exists():
        name = next(project["location"].glob("*.aird")).stem
        natures = {
            "library": "org.polarsys.capella.library.nature",
            "project": "org.polarsys.capella.project.nature",
        }

        if project.get("nature", "") in natures:
            nature = natures[project["nature"]]
        else:
            nature = natures["project"]

        xml = E.projectDescription(
            E.name(name),
            E.comment(),
            E.projects(),
            E.buildSpec(),
            E.natures(E.nature(nature)),
        )

        project_description_file.write_bytes(ET.tostring(xml))


def import_project(project: dict[str, str]) -> None:
    log.info("Loading project into workspace: %s", str(project["location"]))
    importProject(str(project["location"]))
    log.info("Loading of project was successful: %s", str(project["location"]))


if __name__ == "__main__":
    projects = fetch_projects_from_environment()
    print("---START_LOAD_MODEL---")
    try:
        for project in projects:
            clone_git_model(project)
            resolve_entrypoint(project)
            generate_project_file(project)
            import_project(project)
        print("---FINISH_LOAD_MODEL---")
    except Exception as e:
        print("---FAILURE_LOAD_MODEL---")
        raise e
    disable_welcome_screen()
