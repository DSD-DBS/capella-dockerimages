#!/bin/sh

# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

xrdb -merge <<\EOF
Xft.dpi: 96
EOF

exec openbox-session
