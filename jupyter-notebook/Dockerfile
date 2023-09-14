# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

ARG BASE_IMAGE=base
FROM $BASE_IMAGE

USER root

RUN apt-get update && \
    apt-get install --yes --no-install-recommends \
    git \
    git-lfs \
    libgirepository1.0-dev \
    libcairo2-dev \
    gir1.2-pango-1.0 \
    graphviz \
    nodejs \
    npm && \
    rm -rf /var/lib/apt/lists/*

COPY docker-entrypoint.sh /
COPY requirements_template.txt /etc/skel
RUN chmod +x /docker-entrypoint.sh && \
    mkdir -p "/shared" && chown techuser "/shared"

USER techuser

# Activate virtual environment
RUN python -m venv /home/techuser/.venv

ENV _OLD_VIRTUAL_PATH="$PATH"
ENV VIRTUAL_ENV=/home/techuser/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN python3 -m pip install --no-cache-dir -r /etc/skel/requirements_template.txt jupyterlab jupyter-collaboration && \
    jupyter labextension disable "@jupyterlab/extensionmanager-extension" && \
    jupyter labextension disable "@jupyterlab/apputils-extension:announcements" && \
    mkdir /home/techuser/.jupyter && chown techuser /home/techuser/.jupyter

COPY jupyter_lab_config.py /home/techuser/.jupyter/jupyter_lab_config.py

ENV JUPYTER_PORT=8888
ENV NOTEBOOKS_DIR=/workspace/notebooks

EXPOSE $JUPYTER_PORT

WORKDIR $HOME

ENTRYPOINT ["/docker-entrypoint.sh"]
