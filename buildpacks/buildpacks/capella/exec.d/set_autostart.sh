#!/bin/bash
# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

set -eo pipefail

mkdir -p /home/techuser/.config/openbox
ln -s /layers/capella/meta/autostart /home/techuser/.config/openbox/autostart
