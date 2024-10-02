# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0
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
    "//persistedState[@key='memento' and"
    " contains(@value, 'listeningToWorkbenchPageSelectionEvents')]"
)
WS = "/home/techuser/workspace"

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__file__)

# we do something if it is configured like that to keep with defaults
# and act only, if deviating from defaults has been configured
if os.getenv("CAPELLA_DISABLE_SEMANTIC_BROWSER_AUTO_REFRESH", "0") != "1":
    sys.exit(0)
logger.debug(
    "Identified that the environment variable"
    " `CAPELLA_DISABLE_SEMANTIC_BROWSER_AUTO_REFRESH` is set to `1`."
    " We will disable the auto-refresh of the semantic browser."
)
logger.debug("Expecting the workspace to be at: `%s`", WS)
FILE_PATH = pathlib.Path(
    f"{WS}/.metadata/.plugins/org.eclipse.e4.workbench/workbench.xmi"
)
if not FILE_PATH.is_file():
    logger.debug(
        "File not found: `%s`."
        " Cannot disable auto-refresh of semantic browser.",
        FILE_PATH,
    )
    sys.exit(0)


def main() -> None:
    tree = etree.parse(FILE_PATH)
    root = tree.getroot()
    logger.debug(
        "Searching for XPath expression: `%s` in the file `%s`",
        XPATH_EXPR,
        FILE_PATH,
    )
    hit_elements = root.xpath(XPATH_EXPR, namespaces=NS_MAP)
    if not hit_elements:
        logger.debug("No elements found. Exiting.")
        sys.exit(0)
    # runtime lands here, when we found a setting that controls if the semantic
    # browser should auto-refresh or not
    persisted_state = hit_elements[0]
    parent_element = persisted_state.getparent()
    if parent_element is None:
        sys.exit(0)
    if "elementId" not in parent_element.attrib:
        sys.exit(0)
    if "semanticbrowser" not in parent_element.attrib["elementId"].lower():
        sys.exit(0)
    # get line number of the element we want to modify
    browser_autorefresh_line_no = persisted_state.sourceline
    logger.debug(
        "Found element at line number: `%d`", browser_autorefresh_line_no
    )
    line_no = 0
    old = new = None
    for line in fileinput.input(FILE_PATH, inplace=True):
        line_no += 1
        if line_no == browser_autorefresh_line_no:
            old = "listeningToWorkbenchPageSelectionEvents=&quot;1&quot;"
            new = "listeningToWorkbenchPageSelectionEvents=&quot;0&quot;"
            if old in line:
                line = line.replace(old, new)
            else:
                old = new = None
        sys.stdout.write(line)
    fileinput.close()
    if old is not None:
        logger.debug(
            "Replaced `%s` with `%s` in file `%s` at line number %d.",
            old,
            new,
            FILE_PATH,
            browser_autorefresh_line_no,
        )


if __name__ == "__main__":
    main()
