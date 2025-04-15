#!/bin/bash

# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

set -euo pipefail

mkdir -p "$WORKSPACE_DIR"

[[ -z "$JUPYTER_ADDITIONAL_DEPENDENCIES" ]] || uv pip install -U $JUPYTER_ADDITIONAL_DEPENDENCIES 2>&1 | tee -a "$WORKSPACE_DIR/installlog.txt"
unset JUPYTER_ADDITIONAL_DEPENDENCIES

test -f "$WORKSPACE_DIR/requirements.txt" || cp /etc/skel/requirements_template.txt "$WORKSPACE_DIR/requirements.txt"

if ! uv pip install -U -r "$WORKSPACE_DIR/requirements.txt" -r /etc/skel/requirements_template.txt 2>&1 | tee -a "$WORKSPACE_DIR/installlog.txt"; then
    echo "Failed to install requirements.txt, check for invalid packages" | tee -a "$WORKSPACE_DIR/installlog.txt"
fi

test -d "$WORKSPACE_DIR/shared" || ln -s /shared "$WORKSPACE_DIR/shared"

# Patch certifi to find all preloaded certificates
cat /etc/ssl/certs/*.pem > "$(python -m certifi)"

exec /opt/.venv/bin/supervisord
