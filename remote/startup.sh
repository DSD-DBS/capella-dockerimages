#!/bin/bash

# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

set -exuo pipefail

if [ "$(whoami)" == "root" ] || [ "$(whoami)" == "techuser" ];
then
    salt=$(openssl rand -base64 16)
    password_hash=$(openssl passwd -6 -salt ${salt} "${RMT_PASSWORD:?}")
    line=$(grep techuser /etc/shadow);
    echo ${line%%:*}:${password_hash}:${line#*:*:} > /etc/shadow;
else
    echo "Only techuser and root are supported as users.";
    exit 1;
fi

# Replace Variables in the nginx.conf
sed -i "s|__XPRA_SUBPATH__|${XPRA_SUBPATH:-/}|g" /etc/nginx/nginx.conf
sed -i "s|__XPRA_TOKEN__|${RMT_PASSWORD:-/}|g" /etc/nginx/nginx.conf
sed -i "s|__XPRA_CSP_ORIGIN_HOST__|${XPRA_CSP_ORIGIN_HOST:-}|g" /etc/nginx/nginx.conf

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
    source $filename
done

# Load supervisord configuration for connection method
SUPERVISORD_CONFIG_PATH=/tmp/supervisord/supervisord.${CONNECTION_METHOD:-xrdp}.conf
if [ -f "$SUPERVISORD_CONFIG_PATH" ]; then
    echo "Adding '$SUPERVISORD_CONFIG_PATH' to configuration."
    cat $SUPERVISORD_CONFIG_PATH >> /etc/supervisord.conf
else
    echo "No '$SUPERVISORD_CONFIG_PATH' found'. Falling back to xrdp configuration."
    cat /tmp/supervisord/supervisord.xrdp.conf >> /etc/supervisord.conf
fi

exec supervisord
