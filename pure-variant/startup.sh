#!/bin/bash
# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

mkdir -p /workspace/.metadata/.plugins/org.eclipse.core.runtime/.settings/
echo licenseServerLocation="$FLOATING_LICENSE_SERVER" >> /workspace/.metadata/.plugins/org.eclipse.core.runtime/.settings/com.ps.consul.eclipse.ui.float.prefs

# Wait until script is available
until [ "$(ls /opt/scripts)" ]
do
    echo "No scripts are available. Retry in 5 seconds.";
    sleep 5;
done

echo "Found the following scripts: $(ls /opt/scripts)"
sleep 5;
Xvfb :99 -screen 0 1920x1080x8 -nolisten tcp &
/opt/capella/capella -data $EASE_WORKSPACE || r=$?

if [[ -n "$r" ]] && [[ "$r" == 158 || "$r" == 0 ]]; then exit 0; else exit 1; fi
