#!/bin/bash
# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

export DISPLAY=":99"
python3 /opt/setup/set_memory_flags.py
(Xvfb ${DISPLAY} -screen 0 1920x1080x8 -nolisten tcp 0>/dev/null 2>&1 &)
/opt/capella/capella "$@"
