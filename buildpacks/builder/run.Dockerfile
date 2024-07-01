
# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

ARG BASE_IMAGE=debian:bookworm-slim
FROM $BASE_IMAGE

ARG TECHUSER_USER_ID=1001
RUN useradd -l -m -u $TECHUSER_USER_ID techuser && chown techuser /home/techuser
ENV HOME=/home/techuser

USER techuser
