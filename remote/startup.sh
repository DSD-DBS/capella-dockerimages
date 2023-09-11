#!/bin/bash

# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

set -e
if [ "$(whoami)" == "root" ] || [ "$(whoami)" == "techuser" ];
then
    line=$(grep techuser /etc/shadow);
    echo ${line%%:*}:$(openssl passwd -6 -salt $(openssl rand -base64 16) $RMT_PASSWORD):${line#*:*:} > /etc/shadow;
else
    echo "Only techuser and root are supported as users.";
    exit 1;
fi

unset RMT_PASSWORD

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
