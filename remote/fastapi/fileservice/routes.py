# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import os
import pathlib
import secrets

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from . import core
from .models import FileTree

router = APIRouter()
security = HTTPBasic()


@router.get("/workspaces/files", response_model=FileTree)
async def get_files(
    show_hidden: bool, credentials: HTTPBasicCredentials = Depends(security)
):
    if not secrets.compare_digest(
        credentials.password, os.environ["FILESERVICE_PASSWORD"]
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
            headers={"WWW-Authenticate": "Basic"},
        )

    return core.get_files(dir=pathlib.PosixPath("/workspace"), show_hidden=show_hidden)
