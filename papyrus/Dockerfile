# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

ARG BASE_IMAGE=base
FROM $BASE_IMAGE
ENV DEBIAN_FRONTEND=noninteractive

SHELL ["/bin/bash", "-euo", "pipefail", "-c"]
ENV SHELL=/bin/bash

ARG ECLIPSE_REPOSITORY=https://download.eclipse.org

USER root

ARG PAPYRUS_VERSION
COPY ./versions/${PAPYRUS_VERSION}/papyrus.tar.gz /opt/

WORKDIR /opt/
RUN tar -xf papyrus.tar.gz && \
    rm -rf papyrus.tar.gz

ARG MEMORY_LIMIT=5500m

RUN mkdir -p /workspace; \
    # Set workspace permissions
    chown -R techuser /workspace && \
    chmod +x Papyrus/papyrus && \
    sed -i "s/-Xmx[^ ]*/-Xmx$MEMORY_LIMIT/g" /opt/Papyrus/papyrus.ini

# Install SysML
RUN /opt/Papyrus/papyrus \
    -consoleLog \
    -application org.eclipse.equinox.p2.director \
    -noSplash \
    -repository ${ECLIPSE_REPOSITORY}/modeling/mdt/papyrus/components/sysml16/releases/2.2.0_c/p2/ \
    -installIU "org.eclipse.papyrus.sysml16.elementgroup.feature.feature.group,org.eclipse.papyrus.sysml16.feature.feature.group,org.eclipse.papyrus.sysml16.requirements.extension.feature.feature.group"

COPY ./autostart /home/techuser/.config/openbox/autostart

ENV AUTOSTART_PAPYRUS=1
ENV RESTART_PAPYRUS=1

ENV ECLIPSE_INSTALLATION_PATH=/opt/Papyrus
ENV ECLIPSE_EXECUTABLE=/opt/Papyrus/papyrus

ENV BASE_TYPE=papyrus

USER techuser
