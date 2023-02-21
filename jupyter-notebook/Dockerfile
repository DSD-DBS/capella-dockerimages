# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

ARG BASE_IMAGE=base
FROM $BASE_IMAGE

RUN apt update && \
    apt install --yes --no-install-recommends \
    git \
    git-lfs \
    libgirepository1.0-dev \
    libcairo2-dev \
    gir1.2-pango-1.0 \
    graphviz && \
    rm -rf /var/lib/apt/lists/*

COPY docker-entrypoint.sh /
COPY requirements_template.txt /etc/skel

RUN chmod +x /docker-entrypoint.sh && \
    python3 -m pip install jupyterlab capellambse

ENV JUPYTER_PORT=8888
ENV NOTEBOOKS_DIR=/workspace/notebooks

EXPOSE $JUPYTER_PORT

USER techuser
WORKDIR $HOME

ENTRYPOINT "/docker-entrypoint.sh"
