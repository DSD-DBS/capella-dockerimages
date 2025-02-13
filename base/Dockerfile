
# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

ARG BASE_IMAGE=debian:bookworm-slim
FROM $BASE_IMAGE

USER root

SHELL ["/bin/bash", "-euo", "pipefail", "-c"]
ENV SHELL=/bin/bash

RUN apt-get update && \
    apt-get upgrade --yes && \
    apt-get install --yes --no-install-recommends \
    gettext-base \
    git-lfs \
    gnupg \
    locales \
    neovim \
    openssh-client \
    python3 \
    python3-pip \
    python3-venv \
    unzip \
    wget \
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

COPY --chmod=755 hooks/* /opt/git/global-hooks/

WORKDIR /opt/git/global-hooks

RUN ln -s "$(which python3.11)" /usr/bin/python \
    && ln -sf "$(which python3.11)" /usr/bin/python3 \
    && ln -sf "$(which pip3.11)" /usr/local/bin/pip \
    && ln -sf "$(which pip3.11)" /usr/local/bin/pip3 \
    && python -m venv /opt/.venv \
    && pip install --no-cache-dir \
        pre-commit \
        lxml \
        PyYAML \
        certifi \
    && echo "commit-msg post-rewrite pre-commit pre-merge-commit pre-rebase prepare-commit-msg" | xargs -n 1 cp /opt/git/global-hooks/+pre-commit-only.sh \
    && echo "pre-push post-checkout post-commit post-merge" | xargs -n 1 cp /opt/git/global-hooks/+pre-commit-and-lfs.sh \
    && git config --global core.hooksPath /opt/git/global-hooks \
    && chmod -R 755 /opt/git/global-hooks \
    && chown -R techuser /opt/.venv/bin/ /opt/.venv/lib/python3.11/site-packages \
    && cat /etc/ssl/certs/*.pem > "$(python -m certifi)"

# Make pre-commit cache persistent
ENV PRE_COMMIT_HOME=/workspace/.pre-commit

ENV WORKSPACE_DIR=/workspace
WORKDIR /workspace

USER techuser
