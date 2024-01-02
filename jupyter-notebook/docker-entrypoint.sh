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

test -f "$WORKSPACE_DIR/requirements.txt" || cp /etc/skel/requirements_template.txt "$WORKSPACE_DIR/requirements.txt"
pip install -U -r "$WORKSPACE_DIR/requirements.txt" -r /etc/skel/requirements_template.txt 2>&1 | tee "$WORKSPACE_DIR/installlog.txt"

test -d "$WORKSPACE_DIR/shared" || ln -s /shared "$WORKSPACE_DIR/shared"

echo "---START_SESSION---"

exec jupyter-lab --ip=0.0.0.0 \
    --port=$JUPYTER_PORT \
    --no-browser \
    --ServerApp.authenticate_prometheus=False \
    --ServerApp.base_url="$JUPYTER_BASE_URL" \
    --ServerApp.root_dir="$WORKSPACE_DIR"
