#!/bin/bash

# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

set -euo pipefail

case ${1:-startup} in
  backup)
    xvfb-run python /opt/scripts/backup.py
    ;;

  export)
    xvfb-run python /opt/scripts/export.py
    ;;

  startup)
    /startup.sh
    ;;

  *)
    echo Unknown command: $1 >&2
    exit 1
    ;;
esac
