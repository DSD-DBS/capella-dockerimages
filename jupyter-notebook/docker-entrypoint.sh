#!/bin/sh

# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

echo "---START_PREPARE_WORKSPACE---"

mkdir -p "$NOTEBOOKS_DIR"

test -f "$NOTEBOOKS_DIR/requirements.txt" || cp /etc/skel/requirements_template.txt "$NOTEBOOKS_DIR/requirements.txt"
pip install -r "$NOTEBOOKS_DIR/requirements.txt" 2>&1 | tee "$NOTEBOOKS_DIR/installlog.txt"

echo "---START_SESSION---"

jupyter-lab --ip=0.0.0.0 \
    --port=$JUPYTER_PORT \
    --no-browser \
    --ServerApp.authenticate_prometheus=False \
    --ServerApp.base_url="$JUPYTER_BASE_URL" \
    --ServerApp.root_dir="$NOTEBOOKS_DIR"
