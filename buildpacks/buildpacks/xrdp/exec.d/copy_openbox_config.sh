#!/bin/bash

# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

set -eo pipefail

cp /layers/xrdp/app/rc.xml /etc/xdg/openbox/rc.xml
cp /layers/xrdp/app/menu.xml /etc/xdg/openbox/menu.xml
