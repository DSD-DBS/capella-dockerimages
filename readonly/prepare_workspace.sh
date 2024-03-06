#!/bin/bash

# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

set -exuo pipefail

echo "---START_PREPARE_WORKSPACE---"
xvfb-run /opt/capella/capella -clean -data ${WORKSPACE_DIR:-/workspace} --launcher.suppressErrors -nosplash -consolelog -application org.eclipse.ease.runScript -script "file:/opt/scripts/load_models.py";
if [[ "$?" == 0 ]]
then
    echo "---FINISH_PREPARE_WORKSPACE---"
else
    echo "---FAILURE_PREPARE_WORKSPACE---"
    exit 1;
fi

unset GIT_USERNAME GIT_PASSWORD GIT_ASKPASS GIT_REPOS_JSON

echo "---START_SESSION---"
