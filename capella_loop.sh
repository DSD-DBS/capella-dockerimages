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

for version in $CAPELLA_VERSIONS
do
    echo "Running target for Capella version $version..."
    export CAPELLA_VERSION=$version
    export DOCKER_TAG=$CAPELLA_VERSION-$CAPELLA_DOCKERIMAGES_REVISION
    /bin/sh "$@"
    echo "Successfully ran target for Capella version $version."
done
