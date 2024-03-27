#!/bin/bash

# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

set -euo pipefail

case ${1:-startup} in
  backup)
    xvfb-run /opt/t4c_cli/.venv/bin/backup
    ;;

  export)
    xvfb-run /opt/t4c_cli/.venv/bin/exporter
    ;;

  startup)
    /startup.sh
    ;;

  *)
    echo Unknown command: $1 >&2
    exit 1
    ;;
esac
