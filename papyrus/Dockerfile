# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

ARG BASE_IMAGE=base
FROM $BASE_IMAGE
ENV DEBIAN_FRONTEND=noninteractive

SHELL ["/bin/bash", "-euo", "pipefail", "-c"]
ENV SHELL=/bin/bash

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

COPY ./autostart /home/techuser/.config/openbox/autostart

ENV AUTOSTART_PAPYRUS=1
ENV RESTART_PAPYRUS=1

ENV ECLIPSE_INSTALLATION_PATH=/opt/Papyrus
ENV ECLIPSE_EXECUTABLE=/opt/Papyrus/papyrus

ENV BASE_TYPE=papyrus

USER techuser
