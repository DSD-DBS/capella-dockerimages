
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
    neovim \
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
RUN useradd -l -m -u $UID techuser && \
    echo "techuser:tmp_passwd" | chpasswd \
    && chown techuser /home/techuser
ENV HOME=/home/techuser


# This in analogous to the virtualenv activate script
# To allow deactivation of the virtualenv, we need to save the old PATH
ENV _OLD_VIRTUAL_PATH="$PATH"
ENV VIRTUAL_ENV=/opt/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN ln -s "$(which python3.11)" /usr/bin/python && \
    ln -sf "$(which python3.11)" /usr/bin/python3 && \
    ln -sf "$(which pip3.11)" /usr/local/bin/pip && \
    ln -sf "$(which pip3.11)" /usr/local/bin/pip3 && \
    python -m venv /opt/.venv && \
    chmod -R 777 /opt/.venv/bin/ && \
    chmod -R 777 /opt/.venv/lib/python3.11/site-packages

USER techuser
