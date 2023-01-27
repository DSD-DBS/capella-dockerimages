# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

ARG BASE_IMAGE=capella/base
FROM ${BASE_IMAGE}

ARG CAPELLA_VERSION=""

SHELL ["/bin/bash", "-euo", "pipefail", "-c"]
ENV SHELL=/bin/bash

# Install T4C
COPY ./updateSite/$CAPELLA_VERSION /opt/updateSite
WORKDIR /opt/updateSite
RUN chmod +r $(ls /opt/updateSite/*.zip)

USER techuser
## Install T4C Plugins via the P2 API from Eclipse
RUN T4C_ZIP=$(find . -type f -iname "*.zip" | head -n 1 | cut -c 3-); \
    /opt/capella/capella \
    -consoleLog \
    -application org.eclipse.equinox.p2.director \
    -noSplash \
    -repository jar:file:///opt/updateSite/$T4C_ZIP!/ \
    -installIU com.thalesgroup.mde.melody.collab.feature.feature.group,com.thalesgroup.mde.melody.collab.maintenance.feature.feature.group,com.thalesgroup.mde.melody.collab.licbranding.feature.feature.group && \
    chown -R techuser /opt/capella/configuration
USER root

COPY setup_workspace.py /opt/setup/setup_t4c_client.py

RUN chown techuser /opt/capella/capella.ini && \
    echo '-DOBEO_LICENSE_SERVER_CONFIGURATION=$T4C_LICENCE_SECRET \n-Duser.name=$T4C_USERNAME' >> /opt/capella/capella.ini

WORKDIR /opt
ENV BASE_TYPE=t4c
