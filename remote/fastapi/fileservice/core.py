# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import logging
import pathlib

from .models import FileTree, FileType

logger = logging.getLogger("core")


def get_files(dir: pathlib.PosixPath, show_hidden: bool) -> FileTree:
    file = FileTree(
        path=str(dir.absolute()),
        name=dir.name,
        type=FileType.DIRECTORY,
        children=[],
    )

    assert isinstance(file.children, list)

    for item in dir.iterdir():
        if not show_hidden and item.name.startswith("."):
            continue
        if item.is_dir():
            file.children.append(get_files(item, show_hidden))
        elif item.is_file():
            file.children.append(
                FileTree(
                    name=item.name,
                    path=str(item.absolute()),
                    type=FileType.FILE,
                )
            )
        else:
            logger.info(
                "Unsupported file type for file %s. Only directory and file are supported.",
                str(file),
            )

    return file
