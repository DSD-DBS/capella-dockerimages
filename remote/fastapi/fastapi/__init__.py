# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

# SPDX-FileCopyrightText: Copyright DB Netz AG and the fastapi contributors
# SPDX-License-Identifier: Apache-2.0

"""The fastapi package."""
from importlib import metadata

try:
    __version__ = metadata.version("fastapi")
except metadata.PackageNotFoundError:
    __version__ = "0.0.0+unknown"
del metadata
