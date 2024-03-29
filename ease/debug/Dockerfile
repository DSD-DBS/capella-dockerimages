# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

ARG BASE_IMAGE=capella/ease/remote
FROM $BASE_IMAGE

USER root

SHELL ["/bin/bash", "-euo", "pipefail", "-c"]

RUN apt-get update && apt-get install -y wget
ARG NETWORK_ACCESS=unrestricted

COPY libs /tmp/libs
RUN if [ "$NETWORK_ACCESS" = "restricted" ]; then \
    apt-get update && \
    find /tmp/libs -iname "*.deb" -exec apt-get install -y {} \; ; \
    else \
    wget -qO - https://gitlab.com/paulcarroty/vscodium-deb-rpm-repo/raw/master/pub.gpg \
    | gpg --dearmor \
    | dd of=/usr/share/keyrings/vscodium-archive-keyring.gpg && \
    echo 'deb [ signed-by=/usr/share/keyrings/vscodium-archive-keyring.gpg ] https://download.vscodium.com/debs vscodium main' \
    | tee /etc/apt/sources.list.d/vscodium.list && \
    apt-get update && apt-get install -y codium; \
    fi && \
    rm -rf /var/lib/apt/lists/* && \
    rm -r /tmp/libs;

USER techuser
