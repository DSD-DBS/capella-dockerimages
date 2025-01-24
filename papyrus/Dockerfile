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

COPY set_memory_flags.py /opt/setup/set_memory_flags.py
RUN mkdir -p /workspace; \
    # Set workspace permissions
    chown -R techuser /workspace && \
    chmod +x Papyrus/papyrus && \
    chown techuser /opt/Papyrus/papyrus.ini

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

# Set memory options for the JVM (used by set_memory_flags.py)
ARG MEMORY_MAX=90%
ENV MEMORY_MAX=${MEMORY_MAX}
ARG MEMORY_MIN=70%
ENV MEMORY_MIN=${MEMORY_MIN}

ENV BASE_TYPE=papyrus
ENV DISPLAY_NAME="Papyrus $PAPYRUS_VERSION"

USER techuser
