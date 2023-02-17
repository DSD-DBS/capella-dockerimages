#!/bin/bash
# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-dockerimages contributors
# SPDX-License-Identifier: Apache-2.0

if [[ -n "/opt/updateSite/patch_info.csv" ]];
then
    while IFS="," read -r t4c_patch_zip install_iu tag
    do
        /opt/capella/capella \
        -consoleLog \
        -application org.eclipse.equinox.p2.director \
        -profile DefaultProfile \
        -tag $tag \
        -noSplash \
        -repository jar:file:///opt/updateSite/$t4c_patch_zip!/ \
        -installIU $install_iu && \
        chown -R techuser /opt/capella/configuration;
    done < /opt/updateSite/patch_info.csv
fi;
