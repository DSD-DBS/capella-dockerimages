# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

ARG BASE_IMAGE=t4c/client/base
FROM $BASE_IMAGE

ARG CAPELLA_VERSION
ENV CAPELLA_VERSION=${CAPELLA_VERSION}

SHELL ["/bin/bash", "-euo", "pipefail", "-c"]
ENV SHELL=/bin/bash

USER root

# Otherwise, xvfb runs with PID 1 and signal USR1 is not handled properly
# -> xvfb wait command doesn't terminate
ADD https://github.com/krallin/tini/releases/download/v0.19.0/tini /tini
RUN chmod +x /tini

RUN apt-get update && \
    apt-get install -y git-lfs xvfb && \
    rm -rf /var/lib/apt/lists/*

COPY git_askpass.py /etc/git_askpass.py
COPY backup.py /opt/scripts/backup.py

ENV DISPLAY :99

WORKDIR /opt/capella

RUN chown -R techuser /opt/capella

USER techuser

ENTRYPOINT [ "/tini", "--", "xvfb-run", "python", "/opt/scripts/backup.py" ]
