# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pathlib
from importlib import metadata

try:
    __version__ = metadata.version("cdi")
except metadata.PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0+unknown"
del metadata

_repository_root = pathlib.Path(__file__).parent.parent.parent
