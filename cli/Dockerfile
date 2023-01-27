# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

ARG BASE_IMAGE=capella/base
FROM $BASE_IMAGE

SHELL ["/bin/bash", "-euo", "pipefail", "-c"]
ENV SHELL=/bin/bash

RUN apt-get update && \
    apt-get install --yes xdg-utils xvfb && \
    rm -rf /var/lib/apt/lists/*

COPY startup.sh /startup.sh
ENTRYPOINT [ "/startup.sh" ]
