
# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

ARG BASE_IMAGE=alpine
FROM $BASE_IMAGE

USER root

RUN apk add --no-cache \
    shadow \
    bash \
    gettext \
    python3 \
    py3-pip \
    git \
    git-lfs \
    unzip \
    neovim \
    zip \
    wget

SHELL ["/bin/bash", "-euo", "pipefail", "-c"]
ENV SHELL=/bin/bash

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

RUN python -m venv /opt/.venv && \
    # Configure pre-commit
    pip install --no-cache-dir pre-commit lxml PyYAML --no-cache-dir && \
    echo "commit-msg post-rewrite pre-commit pre-merge-commit pre-rebase prepare-commit-msg" | xargs -n 1 cp /opt/git/global-hooks/+pre-commit-only.sh && \
    echo "pre-push post-checkout post-commit post-merge" | xargs -n 1 cp /opt/git/global-hooks/+pre-commit-and-lfs.sh && \
    git config --global core.hooksPath /opt/git/global-hooks && \
    chmod -R 755 /opt/git/global-hooks && \
    chown -R techuser /opt/.venv/bin/ /opt/.venv/lib/*/site-packages

# Make pre-commit cache persistent
ENV PRE_COMMIT_HOME=/workspace/.pre-commit

ENV WORKSPACE_DIR=/workspace
WORKDIR /workspace

USER techuser
