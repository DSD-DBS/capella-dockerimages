# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

ARG BASE_IMAGE=capella/ease/remote
FROM $BASE_IMAGE

USER root

SHELL ["/bin/bash", "-euo", "pipefail", "-c"]

RUN apt-get update && apt-get install -y wget
ARG NETWORK_ACCESS=unrestricted

COPY libs /tmp/libs
# hadolint ignore=SC2046
RUN if [ "$NETWORK_ACCESS" = "restricted" ]; then \
    apt-get update && \
    apt-get install -y $(find /tmp/libs -iname "*.deb"); \
    else \
    wget -qO - https://gitlab.com/paulcarroty/vscodium-deb-rpm-repo/raw/master/pub.gpg \
    | gpg --dearmor \
    | dd of=/usr/share/keyrings/vscodium-archive-keyring.gpg && \
    echo 'deb [ signed-by=/usr/share/keyrings/vscodium-archive-keyring.gpg ] https://download.vscodium.com/debs vscodium main' \
    | tee /etc/apt/sources.list.d/vscodium.list && \
    apt-get update && apt install -y codium; \
    fi && \
    rm -rf /var/lib/apt/lists/* && \
    rm -r /tmp/libs;
