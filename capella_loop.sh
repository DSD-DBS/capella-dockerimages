#!/bin/bash
# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

set -e

# This tries to represent a matrix build
# When a Make target uses this shell, the target runs for each CAPELLA_VERSION
# Please make sure to use environment variables instead of Make variables in the targets.
# This applies to the following variables:
# - $$CAPELLA_VERSION instead of $(CAPELLA_VERSION)
# - $$DOCKER_TAG instead of $(DOCKER_TAG)

ASCII_BOLD="\033[1m"
ASCII_GREEN="\033[0;32m"
ASCII_RED="\033[0;31m"
ASCII_CYAN="\033[0;36m"
ASCII_RESET="\033[0m"

for version in $CAPELLA_VERSIONS
do
    printf "${ASCII_BOLD}${ASCII_CYAN}Running target '$MAKE_CURRENT_TARGET' for Capella version $version...${ASCII_RESET}\n" >&2
    export CAPELLA_VERSION=$version
    export DOCKER_TAG=$(echo "$DOCKER_TAG_SCHEMA" | envsubst)
    /bin/bash -euo pipefail "$@" || r=$?
    if [[ -z "$r" ]]; then
        printf "${ASCII_BOLD}${ASCII_GREEN}Successfully ran target '$MAKE_CURRENT_TARGET' for Capella version $version.${ASCII_RESET}\n" >&2
    else
        printf "${ASCII_BOLD}${ASCII_RED}Running target '$MAKE_CURRENT_TARGET' for Capella version $version failed. Please check the logs above.${ASCII_RESET}\n" >&2
        exit $r
    fi
done
