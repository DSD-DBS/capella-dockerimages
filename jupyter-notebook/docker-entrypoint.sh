#!/bin/bash

# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

handle_exit() {
    exit_status=$?
    if [ $exit_status -ne 0 ]; then
        echo "---FAILURE_PREPARE_WORKSPACE---"
    fi
}
trap handle_exit EXIT

set -euo pipefail

echo "---START_PREPARE_WORKSPACE---"

mkdir -p "$WORKSPACE_DIR"

[[ -z "$JUPYTER_ADDITIONAL_DEPENDENCIES" ]] || uv pip install -U $JUPYTER_ADDITIONAL_DEPENDENCIES 2>&1 | tee -a "$WORKSPACE_DIR/installlog.txt"
unset JUPYTER_ADDITIONAL_DEPENDENCIES

test -f "$WORKSPACE_DIR/requirements.txt" || cp /etc/skel/requirements_template.txt "$WORKSPACE_DIR/requirements.txt"
uv pip install -U -r "$WORKSPACE_DIR/requirements.txt" -r /etc/skel/requirements_template.txt 2>&1 | tee -a "$WORKSPACE_DIR/installlog.txt"

test -d "$WORKSPACE_DIR/shared" || ln -s /shared "$WORKSPACE_DIR/shared"

echo "---START_SESSION---"
exec /opt/.venv/bin/supervisord
