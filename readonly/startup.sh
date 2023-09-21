#!/bin/bash

# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

set -exuo pipefail

salt=$(openssl rand -base64 16)
password_hash=$(openssl passwd -6 -salt ${salt} "${RMT_PASSWORD:?}")
line=$(grep techuser /etc/shadow);
echo ${line%%:*}:${password_hash}:${line#*:*:} > /etc/shadow;
unset RMT_PASSWORD

# Prepare Workspace
echo "---START_PREPARE_WORKSPACE---"
export DISPLAY=:99
xvfb-run /opt/capella/capella -clean -data /workspace --launcher.suppressErrors -nosplash -consolelog -application org.eclipse.ease.runScript -script "file:/opt/scripts/load_models.py";
if [[ "$?" == 0 ]]
then
    echo "---FINISH_PREPARE_WORKSPACE---"
else
    echo "---FAILURE_PREPARE_WORKSPACE---"
    exit 1;
fi

unset GIT_USERNAME GIT_PASSWORD GIT_ASKPASS GIT_REPOS_JSON

echo "---START_SESSION---"

exec supervisord
