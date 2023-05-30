# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

ARG BASE_IMAGE=base
FROM $BASE_IMAGE
ENV DEBIAN_FRONTEND=noninteractive

SHELL ["/bin/bash", "-euo", "pipefail", "-c"]
ENV SHELL=/bin/bash

RUN apt-get update && apt-get install -y openjdk-17-jre

ARG ECLIPSE_VERSION
ARG BUILD_ARCHITECTURE=amd64
COPY ./versions/${ECLIPSE_VERSION}/${BUILD_ARCHITECTURE}/eclipse.tar.gz /opt/

WORKDIR /opt/
RUN ls -la /opt
RUN tar -xf eclipse.tar.gz && \
    rm -rf eclipse.tar.gz

RUN  mkdir /workspace; \
    # Disable Welcome Screen
    mkdir -p /workspace/.metadata/.plugins/org.eclipse.core.runtime/.settings/org.eclipse.ui.prefs; \
    # Set workspace permissions
    chown -R techuser /workspace && \
    chmod +x eclipse/eclipse

COPY ./autostart /home/techuser/.config/openbox/autostart

ENV AUTOSTART_ECLIPSE=1
ENV RESTART_ECLIPSE=1

ENV BASE_TYPE=eclipse
