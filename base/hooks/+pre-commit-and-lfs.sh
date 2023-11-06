#!/bin/bash
# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

STAGE=$(basename "$0")

/opt/git/global-hooks/+pre-commit.sh $STAGE "$@"
exec git lfs $STAGE "${@:2}"
