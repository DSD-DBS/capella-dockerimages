# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

ARG BASE_IMAGE=t4c/client/base
FROM $BASE_IMAGE

USER root

RUN apt-get update && \
    apt-get install -y git-lfs xvfb && \
    rm -rf /var/lib/apt/lists/*

COPY git_askpass.py /etc/git_askpass.py
ENV GIT_ASKPASS=/etc/git_askpass.py
RUN chmod +x /etc/git_askpass.py

COPY importer.sh /opt/capella/importer.sh
COPY backup.sh /opt/capella/backup.sh
COPY startup.sh /opt/capella/startup.sh

ENV DISPLAY :99

WORKDIR /opt/capella

RUN chmod +x /opt/capella/*.sh && \
    chown -R techuser /opt/capella

USER techuser

ENTRYPOINT [ "/opt/capella/startup.sh" ]
