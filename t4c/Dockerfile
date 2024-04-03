# syntax=docker/dockerfile:1.4

# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
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

COPY docker_entrypoint.sh /docker_entrypoint.sh
RUN chmod 555 /docker_entrypoint.sh

ENV DISPLAY :99

WORKDIR /opt/capella

RUN chown -R techuser /opt/capella

# Install T4C
COPY ./updateSite/$CAPELLA_VERSION /opt/updateSite
WORKDIR /opt/updateSite
RUN find /opt/updateSite -type f -name "*.zip" -exec chmod +r {} \;

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

COPY setup_workspace_t4c.py /opt/setup/setup_workspace_t4c.py

RUN cat >> /opt/capella/capella.ini <<EOT && chown techuser /opt/capella/capella.ini
-DOBEO_LICENSE_SERVER_CONFIGURATION=\$T4C_LICENCE_SECRET
-Duser.name=\$T4C_USERNAME
-Dfr.obeo.dsl.viewpoint.collab.import.gmf.notation.keep.cdoid.as.xmiid=true
-Dfr.obeo.dsl.viewpoint.collab.import.other.elements.keep.cdoid.as.xmiid=true
EOT

COPY t4c_cli /opt/t4c_cli/t4c_cli
COPY pyproject.toml /opt/t4c_cli/pyproject.toml

WORKDIR /opt/t4c_cli
RUN python -m venv .venv && source .venv/bin/activate && pip install --no-cache-dir .

WORKDIR /opt
ENV BASE_TYPE=t4c

USER techuser

ENTRYPOINT [ "/tini", "--", "/docker_entrypoint.sh" ]
