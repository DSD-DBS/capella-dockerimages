# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

ARG BASE_IMAGE=capella/base
FROM ${BASE_IMAGE}

ARG CAPELLA_VERSION=""
ENV CAPELLA_VERSION=${CAPELLA_VERSION}

SHELL ["/bin/bash", "-euo", "pipefail", "-c"]
ENV SHELL=/bin/bash

USER root

RUN apt-get update && \
    apt-get install -y git-lfs xvfb xauth && \
    rm -rf /var/lib/apt/lists/*

COPY git_askpass.py /etc/git_askpass.py
RUN chmod 555 /etc/git_askpass.py

COPY docker_entrypoint.sh /docker_entrypoint.sh
RUN chmod 555 /docker_entrypoint.sh

ENV DISPLAY :99

WORKDIR /opt/capella

RUN chown -R techuser /opt/capella

COPY backup.py /opt/scripts/backup.py
COPY export.py /opt/scripts/export.py

# Install T4C
COPY ./updateSite/$CAPELLA_VERSION /opt/updateSite
WORKDIR /opt/updateSite
RUN chmod +r $(ls /opt/updateSite/*.zip)

USER techuser
## Install T4C Plugins via the P2 API from Eclipse
RUN T4C_ZIP=$(find . -type f -iname "com.thalesgroup.mde.melody.team.license.update-*.zip" | head -n 1 | cut -c 3-); \
    /opt/capella/capella \
    -consoleLog \
    -application org.eclipse.equinox.p2.director \
    -noSplash \
    -repository jar:file:///opt/updateSite/$T4C_ZIP!/ \
    -installIU com.thalesgroup.mde.melody.collab.feature.feature.group,com.thalesgroup.mde.melody.collab.maintenance.feature.feature.group,com.thalesgroup.mde.melody.collab.licbranding.feature.feature.group && \
    chown -R techuser /opt/capella/configuration

RUN PATCH_DIR=/opt/updateSite /opt/patch.sh

USER root

COPY setup_workspace.py /opt/setup/setup_t4c_client.py

RUN chown techuser /opt/capella/capella.ini && \
    echo '-DOBEO_LICENSE_SERVER_CONFIGURATION=$T4C_LICENCE_SECRET' >> /opt/capella/capella.ini && \
    echo '-Duser.name=$T4C_USERNAME' >> /opt/capella/capella.ini

WORKDIR /opt
ENV BASE_TYPE=t4c

ENTRYPOINT [ "/tini", "--", "/docker_entrypoint.sh" ]
