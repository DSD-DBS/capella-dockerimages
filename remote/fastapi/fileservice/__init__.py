# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from importlib import metadata

from fastapi import FastAPI

from . import routes

try:
    __version__ = metadata.version("fastapi")
except metadata.PackageNotFoundError:
    __version__ = "0.0.0+unknown"
del metadata

app = FastAPI()

app.include_router(routes.router, prefix="/api/v1")
