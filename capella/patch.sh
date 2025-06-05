#!/bin/bash
# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0
set -euo pipefail

# Installation command complains about empty proxy variables
if [[ "${http_proxy}" == "" ]]; then
    echo "http_proxy is empty, unsetting it"
    unset http_proxy
fi
if [[ "${https_proxy}" == "" ]]; then
    echo "https_proxy is empty, unsetting it"
    unset https_proxy
fi

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
