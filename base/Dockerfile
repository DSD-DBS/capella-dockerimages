
# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

ARG BASE_IMAGE=debian:bookworm-slim
FROM $BASE_IMAGE

USER root

SHELL ["/bin/bash", "-euo", "pipefail", "-c"]
ENV SHELL=/bin/bash

RUN apt-get update && \
    apt-get upgrade --yes && \
    apt-get install --yes \
    gettext-base \
    locales \
    python3 \
    python3-pip \
    python3-venv \
    git-lfs \
    unzip \
    zip && \
    rm -rf /var/lib/apt/lists/*

RUN echo "en_GB.UTF-8 UTF-8" >> /etc/locale.gen && \
    locale-gen en_GB.UTF-8 && \
    update-locale en_GB.UTF-8 && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    echo "LANG=en_GB.UTF-8" >> /etc/default/locale && \
    echo "LANGUAGE=en_GB:en" >> /etc/default/locale && \
    echo "LC_ALL=en_GB.UTF-8" >> /etc/default/locale
ENV LANG="en_GB.UTF-8"
ENV LANGUAGE="en_GB:en"
ENV LC_ALL="en_GB.UTF-8"

# Create techuser with UID
ARG UID=1001
RUN useradd -l -m -u $UID techuser
RUN echo "techuser:tmp_passwd" | chpasswd
ENV HOME=/home/techuser
RUN chown techuser /home/techuser

RUN ln -sf $(which python3) /usr/bin/python
