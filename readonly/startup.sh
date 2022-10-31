#!/bin/bash

# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

set -ex
echo -e "tmp_passwd\n$RMT_PASSWORD\n$RMT_PASSWORD" | passwd
unset RMT_PASSWORD

# Prepare Workspace
echo "---START_PREPARE_WORKSPACE---"
export DISPLAY=:99
Xvfb :99 -screen 0 1920x1080x8 -nolisten tcp &
/opt/capella/capella -clean -data /workspace --launcher.suppressErrors -nosplash -consolelog -application org.eclipse.ease.runScript -script "file:/opt/scripts/load_models.py";
if [[ "$?" == 0 ]]
then
    echo "---FINISH_PREPARE_WORKSPACE---"
else
    echo "---FAILURE_PREPARE_WORKSPACE---"
    exit 1;
fi

pkill Xvfb
unset GIT_USERNAME GIT_PASSWORD GIT_ASKPASS GIT_REPOS_JSON

echo "---START_SESSION---"

exec supervisord
