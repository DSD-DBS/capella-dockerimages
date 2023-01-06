#!/bin/sh
# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-dockerimages contributors
# SPDX-License-Identifier: Apache-2.0
set -e

# This tries to represent a matrix build
# When a Make target uses this shell, the target is run for each CAPELLA_VERSION
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
    echo -e "${ASCII_BOLD}${ASCII_CYAN}Running target '$MAKE_CURRENT_TARGET' for Capella version $version...${ASCII_RESET}"
    export CAPELLA_VERSION=$version
    export DOCKER_TAG=$CAPELLA_VERSION-$CAPELLA_DOCKERIMAGES_REVISION
    /bin/sh "$@" || r=$?
    if [ -z "$r" ]; then
        echo -e "${ASCII_BOLD}${ASCII_GREEN}Successfully ran target '$MAKE_CURRENT_TARGET' for Capella version $version.${ASCII_RESET}"
    else
        echo -e "${ASCII_BOLD}${ASCII_RED}Running target '$MAKE_CURRENT_TARGET' for Capella version $version failed. Please check the logs above.${ASCII_RESET}"
        exit $r
    fi
done
