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

# Run preparation scripts
for filename in /opt/setup/*.py; do
    echo "Executing script '$filename'..."
    python3 $filename
done
stat /opt/setup_workspace_purevariants.py &>/dev/null && python3 /opt/setup_workspace_purevariants.py
stat /inputs/pure-variants/license.lic &>/dev/null \
&& mkdir -p /home/techuser/pure-variants-5/ \
&& cp /inputs/pure-variants/license.lic /home/techuser/pure-variants-5/de.license

# Replace environment variables in capella.ini, e.g. licences
envsubst < /opt/capella/capella.ini > /tmp/capella.ini && mv /tmp/capella.ini /opt/capella/capella.ini;

exec supervisord
