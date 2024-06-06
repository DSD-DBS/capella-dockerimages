# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

ARG BASE_IMAGE=base
FROM $BASE_IMAGE as base

ENV DEBIAN_FRONTEND=noninteractive

SHELL ["/bin/bash", "-euo", "pipefail", "-c"]
ENV SHELL=/bin/bash

USER root
ARG ECLIPSE_REPOSITORY=https://download.eclipse.org

# https://forums.debian.net/viewtopic.php?t=151997
RUN apt-get update && apt-get install -y openjdk-17-jre || apt-get install -y openjdk-17-jre

ARG ECLIPSE_VERSION
ARG BUILD_ARCHITECTURE=amd64
COPY ./versions/${ECLIPSE_VERSION}/${BUILD_ARCHITECTURE}/eclipse.tar.gz /opt/

WORKDIR /opt/
RUN tar -xf eclipse.tar.gz && \
    rm -rf eclipse.tar.gz

RUN mkdir -p /workspace; \
    # Set workspace permissions
    chown -R techuser /workspace && \
    chmod +x eclipse/eclipse && \
    chown -R techuser /opt/eclipse

COPY set_memory_flags.py /opt/setup/set_memory_flags.py

USER techuser

# Install EGit (https://www.eclipse.org/egit/)
RUN /opt/eclipse/eclipse \
    -consoleLog \
    -application org.eclipse.equinox.p2.director \
    -noSplash \
    -repository ${ECLIPSE_REPOSITORY}/egit/updates/ \
    -installIU "org.eclipse.egit,org.eclipse.egit.core,org.eclipse.egit.ui"

USER root

COPY ./autostart /home/techuser/.config/openbox/autostart

ENV AUTOSTART_ECLIPSE=1
ENV RESTART_ECLIPSE=1

ENV ECLIPSE_INSTALLATION_PATH=/opt/eclipse
ENV ECLIPSE_EXECUTABLE=/opt/eclipse/eclipse

# Set memory options for the JVM (used by set_memory_flags.py)
ARG MEMORY_MAX=90%
ENV MEMORY_MAX=${MEMORY_MAX}
ARG MEMORY_MIN=70%
ENV MEMORY_MIN=${MEMORY_MIN}

ENV BASE_TYPE=eclipse

USER techuser
