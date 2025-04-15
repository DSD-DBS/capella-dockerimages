#!/bin/bash
# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0
set -euo pipefail

python3 /opt/setup/set_memory_flags.py

if [ "$USE_VIRTUAL_DISPLAY" = "1" ]; then
    (Xvfb ${DISPLAY} -screen 0 1920x1080x8 -nolisten tcp 0>/dev/null 2>&1 &)
fi
/opt/capella/capella "$@"
