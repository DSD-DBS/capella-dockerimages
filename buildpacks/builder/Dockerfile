# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

# Define the base image
ARG BASE_IMAGE=debian:bookworm-slim
FROM $BASE_IMAGE

USER root

# Install packages that we want to make available at build time
RUN apt-get update && \
  apt-get install -y \
    xz-utils \
    ca-certificates \
    rsync \
    python3 \
    python3-pip \
    python3-venv && \
  rm -rf /var/lib/apt/lists/*

# Set required CNB user information
ARG CNB_USER_ID=1000
ARG CNB_GROUP_ID=1000
ENV CNB_USER_ID=${CNB_USER_ID}
ENV CNB_GROUP_ID=${CNB_GROUP_ID}

# Create user and group
RUN groupadd cnb --gid ${CNB_GROUP_ID} && \
  useradd -l --uid ${CNB_USER_ID} --gid ${CNB_GROUP_ID} -m -s /bin/bash cnb

RUN ln -s "$(which python3.11)" /usr/bin/python && \
  ln -sf "$(which python3.11)" /usr/bin/python3 && \
  ln -sf "$(which pip3.11)" /usr/local/bin/pip && \
  ln -sf "$(which pip3.11)" /usr/local/bin/pip3 && \
  pip install --break-system-packages --no-cache-dir pre-commit lxml PyYAML

# Set user and group
USER ${CNB_USER_ID}:${CNB_GROUP_ID}
