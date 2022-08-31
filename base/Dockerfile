
# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

ARG BASE_IMAGE=debian:bullseye
FROM $BASE_IMAGE
RUN apt-get update && \
    apt-get upgrade --yes && \
    apt-get install --yes \
    python3 \
    python3-pip \
    zip \
    unzip && rm -rf /var/lib/apt/lists/*

# Create techuser with UID
ARG UID=1001
RUN useradd -l -m -u $UID techuser
RUN echo "techuser:tmp_passwd" | chpasswd
ENV HOME=/home/techuser
RUN chown techuser /home/techuser

RUN ln -sf $(which python3) /usr/bin/python
