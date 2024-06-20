#!/bin/bash

# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

set -euo pipefail

case ${1:-startup} in
  backup)
    xvfb-run $VIRTUAL_ENV/bin/backup
    ;;

  export)
    xvfb-run $VIRTUAL_ENV/bin/exporter
    ;;

  startup)
    /startup.sh
    ;;

  *)
    echo Unknown command: $1 >&2
    exit 1
    ;;
esac
