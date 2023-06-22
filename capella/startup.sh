#!/bin/bash
# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

export DISPLAY=":99"
(Xvfb ${DISPLAY} -screen 0 1920x1080x8 -nolisten tcp 0>/dev/null 2>&1 &)
/opt/capella/capella "$@"
