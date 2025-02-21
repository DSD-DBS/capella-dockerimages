# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0
"""Module is documented in the function `main`."""

import fileinput
import logging
import os
import pathlib
import sys

from lxml import etree

NS_MAP = {
    "xmi": "http://www.omg.org/XMI",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    "basic": "http://www.eclipse.org/ui/2010/UIModel/application/ui/basic",
    "advanced": (
        "http://www.eclipse.org/ui/2010/UIModel/application/ui/advanced"
    ),
    "application": "http://www.eclipse.org/ui/2010/UIModel/application",
    "menu": "http://www.eclipse.org/ui/2010/UIModel/application/ui/menu",
}
XPATH_EXPR = (
    "//persistedState[@key='memento'"
    " and contains(@value, 'listeningToWorkbenchPageSelectionEvents')]"
)

WORKSPACE_DIR = os.getenv("WORKSPACE_DIR", "/workspace")

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__file__)


def main() -> None:
    """Disable auto-refresh of semantic browser when setting exists.

    This script will disable the auto-refresh of the semantic browser in
    Capella. A precondition is, that the according Capella configuration
    entry already exists on disk. The script identifies the setting of
    interest using ``lxml`` and an XPath query. The editing of the
    configuration file is done in-place using the ``fileinput`` module
    instead of writing it on disk with ``lxml``. This is done to avoid
    issues with the file format. Capella mixes HTML into an XML file
    and `lxml` escapes some HTML entities, which would break the file.
    """
    _check_environment_variable()
    logger.debug("Expecting the workspace to be at: `%s`", WORKSPACE_DIR)
    file_path = (
        pathlib.Path(WORKSPACE_DIR)
        / ".metadata"
        / ".plugins"
        / "org.eclipse.e4.workbench"
        / "workbench.xmi"
    )
    _check_for_file_existence(file_path)

    browser_autorefresh_line_no = _identify_semantic_browser_line_no(file_path)

    _replace_content_in_line_of_file(
        file_path,
        browser_autorefresh_line_no,
        "listeningToWorkbenchPageSelectionEvents=&quot;1&quot;",
        "listeningToWorkbenchPageSelectionEvents=&quot;0&quot;",
    )


def _check_environment_variable() -> None:
    disable_semantic_browser_auto_refresh = os.getenv(
        "CAPELLA_DISABLE_SEMANTIC_BROWSER_AUTO_REFRESH", "0"
    )
    if disable_semantic_browser_auto_refresh not in ("0", "1"):
        raise ValueError(
            "Unsupported value for environment variable"
            " `CAPELLA_DISABLE_SEMANTIC_BROWSER_AUTO_REFRESH`."
            " Only `0` or `1` are supported."
        )

    if disable_semantic_browser_auto_refresh == "0":
        logger.info(
            "Environment variable"
            " `CAPELLA_DISABLE_SEMANTIC_BROWSER_AUTO_REFRESH` is set to 0."
            " The semantic browser auto refresh will not be disabled. ",
        )
        sys.exit(0)

    logger.info(
        "Identified that the environment variable"
        " `CAPELLA_DISABLE_SEMANTIC_BROWSER_AUTO_REFRESH` is set to `1`."
        " We will disable the auto-refresh of the semantic browser."
    )


def _check_for_file_existence(file_path: pathlib.Path) -> None:
    if not file_path.is_file():
        logger.debug(
            "File not found: `%s`."
            " Cannot disable auto-refresh of semantic browser.",
            file_path,
        )
        sys.exit(0)


def _identify_semantic_browser_line_no(file_path: pathlib.Path) -> int:
    root = etree.parse(file_path).getroot()
    logger.debug(
        "Searching for XPath expression: `%s` in the file `%s`",
        XPATH_EXPR,
        file_path,
    )
    hit_elements = root.xpath(XPATH_EXPR, namespaces=NS_MAP)
    if not hit_elements:
        logger.debug("No elements found. Exiting.")
        sys.exit(0)

    # Runtime lands here, when we found a setting that controls if the semantic
    # browser should auto-refresh or not
    persisted_state = hit_elements[0]
    parent_element = persisted_state.getparent()
    if (
        parent_element is None
        or "elementId" not in parent_element.attrib
        or "semanticbrowser" not in parent_element.attrib["elementId"].lower()
    ):
        sys.exit(0)

    browser_autorefresh_line_no = persisted_state.sourceline
    logger.debug(
        "Found element in line %s:%d",
        file_path,
        browser_autorefresh_line_no,
    )
    return browser_autorefresh_line_no


def _replace_content_in_line_of_file(
    file_path: pathlib.Path, line_no: int, old: str, new: str
) -> None:
    with fileinput.input(file_path, inplace=True, backup=".bak") as file:
        for cur_line_no, line in enumerate(file, start=1):
            if cur_line_no != line_no:
                sys.stdout.write(line)
                continue
            if old in line:
                line = line.replace(old, new)  # noqa: PLW2901
                logger.info(
                    "Replaced `%s` with `%s` in line number: `%d`",
                    old,
                    new,
                    line_no,
                )
            else:
                logger.debug(
                    "Skipping replacement in line '%d' as it does not contain '%s'",
                    cur_line_no,
                    old,
                )
            sys.stdout.write(line)


if __name__ == "__main__":
    main()
