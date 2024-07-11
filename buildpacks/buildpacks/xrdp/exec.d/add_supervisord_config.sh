#!/bin/bash

# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

if [ "${CONNECTION_METHOD:-xrdp}" == "xrdp" ]; then
    cat >> "/layers/supervisord/app/supervisord.conf" << EOL
[program:xrdp]
command=/usr/sbin/xrdp --nodaemon
user=techuser
autorestart=true

[program:xrdp-sesman]
directory=/home/techuser
command=/usr/sbin/xrdp-sesman --nodaemon
user=techuser
autorestart=true
environment=DISPLAY=":10"
EOL
fi
