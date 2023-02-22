#!/bin/bash
# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-dockerimages contributors
# SPDX-License-Identifier: Apache-2.0

if [[ -n "/opt/updateSite/patch_info.csv" ]];
then
    while IFS="," read -r t4c_patch_zip install_iu tag
    do
        INSTALL_IU_JOIN=$(echo $install_iu | sed "s/ /,/g");
        /opt/capella/capella \
        -consoleLog \
        -application org.eclipse.equinox.p2.director \
        -profile DefaultProfile \
        -tag $tag \
        -noSplash \
        -repository jar:file:///opt/updateSite/$t4c_patch_zip!/ \
        -installIU $INSTALL_IU_JOIN && \
        chown -R techuser /opt/capella/configuration;
    done < /opt/updateSite/patch_info.csv
fi;
exit 0;
