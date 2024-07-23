#!/bin/bash
# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0
set -euo pipefail

if [[ -s "${PATCH_DIR:?}/patch_info.csv" ]];
then
    while IFS="," read -r patch_zip install_iu tag
    do
        INSTALL_IU_JOIN=$(echo $install_iu | sed "s/ /,/g");
        /opt/capella/capella \
        -consoleLog \
        -application org.eclipse.equinox.p2.director \
        -profile DefaultProfile \
        -tag "$tag" \
        -noSplash \
        -repository jar:file://${PATCH_DIR:?}/$patch_zip!/ \
        -installIU $INSTALL_IU_JOIN;
    done < ${PATCH_DIR:?}/patch_info.csv
fi;
exit 0;
