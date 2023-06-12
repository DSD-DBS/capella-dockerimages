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
    [ -e "$filename" ] || continue
    echo "Executing Python script '$filename'..."
    python3 $filename
done

for filename in /opt/setup/*.sh; do
    [ -e "$filename" ] || continue
    echo "Executing shell script '$filename'..."
    /bin/bash $filename
done

exec supervisord
