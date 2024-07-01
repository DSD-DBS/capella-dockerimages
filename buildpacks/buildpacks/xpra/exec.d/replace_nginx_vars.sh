#!/bin/bash

# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

# Replace Variables in the nginx.conf
sed -i "s|__XPRA_SUBPATH__|${XPRA_SUBPATH:-/}|g" /layers/xpra/app/nginx.conf
sed -i "s|__XPRA_CSP_ORIGIN_HOST__|${XPRA_CSP_ORIGIN_HOST:-}|g" /layers/xpra/app/nginx.conf
