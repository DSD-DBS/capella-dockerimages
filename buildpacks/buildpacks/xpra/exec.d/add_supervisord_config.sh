#!/bin/bash

# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

if [ "${CONNECTION_METHOD:-xrdp}" == "xpra" ]; then
    cat >> "/layers/supervisord/app/supervisord.conf" << EOL
[program:xpra]
command=xpra start :10 --start=/home/techuser/.config/openbox/autostart --start-env=GTK_IM_MODULE=ibus --attach=yes --daemon=no --bind-tcp=0.0.0.0:10001 --min-quality=70
user=techuser
autorestart=true
environment=DISPLAY=":10",XPRA_DEFAULT_CONTENT_TYPE="text",XPRA_DEFAULT_VFB_RESOLUTION="1920x1080"

[program:nginx]
command=nginx -c /layers/xpra/app/nginx.conf
user=techuser
autorestart=true
EOL
fi
