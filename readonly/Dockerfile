# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

ARG BASE_IMAGE=capella/ease/remote
FROM $BASE_IMAGE

SHELL ["/bin/bash", "-euo", "pipefail", "-c"]
ENV SHELL=/bin/bash

USER root

RUN pip install --no-cache-dir lxml==4.9.3
ENV EASE_LOG_LOCATION=/proc/1/fd/1

COPY load_models.py /opt/scripts/load_models.py
COPY prepare_workspace.sh /opt/setup/prepare_workspace.sh

USER techuser
