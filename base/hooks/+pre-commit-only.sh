#!/bin/bash
# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

exec /opt/git/global-hooks/+pre-commit.sh $(basename "$0") "$@"
