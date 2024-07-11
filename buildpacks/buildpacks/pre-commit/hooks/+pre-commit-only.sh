#!/bin/bash
# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

exec /opt/git/global-hooks/+pre-commit.sh $(basename "$0") "$@"
