# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

ARG BASE_IMAGE=base
FROM $BASE_IMAGE

USER root

SHELL ["/bin/bash", "-euo", "pipefail", "-c"]
ENV SHELL=/bin/bash

RUN apt-get update && \
    apt-get install --yes --no-install-recommends \
    libgirepository1.0-dev \
    libcairo2-dev \
    gir1.2-pango-1.0 \
    curl \
    less \
    weasyprint \
    graphviz && \
    rm -rf /var/lib/apt/lists/*

ENV NVM_DIR=/usr/local/nvm
RUN mkdir ${NVM_DIR} && \
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash && \
    bash -c "source ${NVM_DIR}/nvm.sh && nvm install --lts" && \
    ln -s ${NVM_DIR}/versions/node/*/bin ${NVM_DIR}/bin
ENV PATH="${NVM_DIR}/bin:${PATH}"

COPY docker-entrypoint.sh /
COPY requirements_template.txt /etc/skel
RUN chmod +x /docker-entrypoint.sh && \
    mkdir -p "/shared" && chown techuser "/shared" && \
    chown techuser -R /var/log

USER techuser

RUN pip install --no-cache-dir supervisor requests prometheus_client uv
COPY supervisord.conf /etc/supervisord.conf
COPY jupyter_metrics.py /opt/metrics.py

# Activate virtual environment
RUN uv venv --seed /home/techuser/.venv

ENV _OLD_VIRTUAL_PATH="$PATH"
ENV VIRTUAL_ENV=/home/techuser/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN uv pip install --no-cache -r /etc/skel/requirements_template.txt jupyterlab jupyter-collaboration && \
    jupyter labextension disable "@jupyterlab/extensionmanager-extension" && \
    jupyter labextension disable "@jupyterlab/apputils-extension:announcements" && \
    mkdir /home/techuser/.jupyter && chown techuser /home/techuser/.jupyter

COPY jupyter_lab_config.py /home/techuser/.jupyter/jupyter_lab_config.py
COPY --chown=techuser jupyter_terminal_config.json /home/techuser/.jupyter/lab/user-settings/@jupyterlab/terminal-extension/plugin.jupyterlab-settings

ENV JUPYTER_PORT=8888
ENV WORKSPACE_DIR=/workspace/notebooks

EXPOSE $JUPYTER_PORT

WORKDIR $HOME

ENV JUPYTER_ADDITIONAL_DEPENDENCIES=""

ENTRYPOINT ["/docker-entrypoint.sh"]
