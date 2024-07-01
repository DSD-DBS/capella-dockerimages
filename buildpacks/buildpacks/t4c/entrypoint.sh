#!/bin/bash

# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

set -euo pipefail

case ${1:-startup} in
  backup)
    xvfb-run /layers/t4c/cli/bin/backup
    ;;

  export)
    xvfb-run /layers/t4c/cli/bin/exporter
    ;;

  startup)
    /layers/capella/meta/entrypoint.sh
    ;;

  *)
    echo Unknown command: $1 >&2
    exit 1
    ;;
esac
