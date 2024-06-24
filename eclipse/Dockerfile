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
RUN apk add --no-cache openjdk17

ARG ECLIPSE_VERSION
ARG BUILD_ARCHITECTURE=amd64
COPY ./versions/${ECLIPSE_VERSION}/${BUILD_ARCHITECTURE}/eclipse.tar.gz /opt/

WORKDIR /opt/
RUN tar -xf eclipse.tar.gz && \
    rm -rf eclipse.tar.gz

ARG MEMORY_LIMIT=5500m

RUN mkdir -p /workspace; \
    # Set workspace permissions
    chown -R techuser /workspace && \
    chmod +x eclipse/eclipse && \
    chown -R techuser /opt/eclipse && \
    sed -i "s/-Xmx[^ ]*/-Xmx$MEMORY_LIMIT/g" /opt/eclipse/eclipse.ini

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

ENV BASE_TYPE=eclipse

USER techuser
