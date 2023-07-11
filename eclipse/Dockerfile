# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

ARG BASE_IMAGE=base
ARG BUILD_TYPE=online
FROM $BASE_IMAGE as base

ENV DEBIAN_FRONTEND=noninteractive

SHELL ["/bin/bash", "-euo", "pipefail", "-c"]
ENV SHELL=/bin/bash

FROM base as build_online
ONBUILD ENV EGIT_REPOSITORY=https://download.eclipse.org/egit/updates/

FROM base as build_offline
ONBUILD USER root
ONBUILD ENV EGIT_REPOSITORY=file:/tmp/egit
ONBUILD COPY ./egit /tmp/egit
ONBUILD RUN chown -R techuser /tmp/egit

FROM build_${BUILD_TYPE}

RUN apt-get update && apt-get install -y openjdk-17-jre

ARG ECLIPSE_VERSION
ARG BUILD_ARCHITECTURE=amd64
COPY ./versions/${ECLIPSE_VERSION}/${BUILD_ARCHITECTURE}/eclipse.tar.gz /opt/

WORKDIR /opt/
RUN tar -xf eclipse.tar.gz && \
    rm -rf eclipse.tar.gz

RUN mkdir /workspace; \
    # Disable Welcome Screen
    mkdir -p /workspace/.metadata/.plugins/org.eclipse.core.runtime/.settings/org.eclipse.ui.prefs; \
    # Set workspace permissions
    chown -R techuser /workspace && \
    chmod +x eclipse/eclipse && \
    chown -R techuser /opt/eclipse

USER techuser

# Install EGit (https://www.eclipse.org/egit/)
RUN /opt/eclipse/eclipse \
    -consoleLog \
    -application org.eclipse.equinox.p2.director \
    -noSplash \
    -repository ${EGIT_REPOSITORY} \
    -installIU "org.eclipse.egit,org.eclipse.egit.core,org.eclipse.egit.ui"

USER root

COPY ./autostart /home/techuser/.config/openbox/autostart

ENV AUTOSTART_ECLIPSE=1
ENV RESTART_ECLIPSE=1

ENV ECLIPSE_INSTALLATION_PATH=/opt/eclipse
ENV ECLIPSE_EXECUTABLE=/opt/eclipse/eclipse

ENV BASE_TYPE=eclipse
