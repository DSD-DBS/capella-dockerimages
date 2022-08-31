# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import enum
import typing as t

from pydantic import BaseModel


class FileType(enum.Enum):
    FILE = "file"
    DIRECTORY = "directory"


class FileTree(BaseModel):
    path: str
    name: str
    type: FileType
    children: t.Optional[list[FileTree]]

    class Config:
        orm_mode = True
