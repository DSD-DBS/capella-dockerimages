#!/bin/bash

# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

set -eo pipefail

if [ "${CONNECTION_METHOD:-xrdp}" == "xrdp" ];
then
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
fi
