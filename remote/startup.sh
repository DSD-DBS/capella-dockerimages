#!/bin/bash

# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

set -e
if [ "$(whoami)" == "root" ];
then
    echo -e "$RMT_PASSWORD\n$RMT_PASSWORD" | passwd techuser;
elif [ "$(whoami)" == "techuser" ];
then
    echo -e "tmp_passwd\n$RMT_PASSWORD\n$RMT_PASSWORD" | passwd;
else
    echo "Only techuser and root are supported as users.";
    exit 1;
fi

python3 /opt/setup_workspace.py;
stat /opt/setup_workspace_purevariants.py &>/dev/null && python3 /opt/setup_workspace_purevariants.py

# Replace environment variables in capella.ini, e.g. licences
envsubst < /opt/capella/capella.ini > /tmp/capella.ini && mv /tmp/capella.ini /opt/capella/capella.ini;

exec supervisord
