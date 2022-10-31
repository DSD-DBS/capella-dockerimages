# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

ARG BASE_IMAGE=capella/ease/remote
FROM $BASE_IMAGE

USER root

RUN pip install lxml
COPY load_models.py /opt/scripts/load_models.py
RUN chown -R techuser /opt/capella
ENV EASE_LOG_LOCATION=/proc/1/fd/1

COPY startup.sh /home/techuser/.startup.sh
RUN chmod +x /home/techuser/.startup.sh

USER techuser
ENTRYPOINT [ "/home/techuser/.startup.sh" ]
