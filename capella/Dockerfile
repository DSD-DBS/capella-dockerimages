# syntax=docker/dockerfile:1.10.0
# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0
ARG BASE_IMAGE=base
ARG BUILD_TYPE=online
FROM ${BASE_IMAGE} AS base

ENV DEBIAN_FRONTEND=noninteractive

SHELL ["/bin/bash", "-euo", "pipefail", "-c"]
ENV SHELL=/bin/bash

USER root
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libjavascriptcoregtk-4.0-18 \
    libwebkit2gtk-4.0-37 && \
    rm -rf /var/lib/apt/lists/*;

WORKDIR /opt/
USER techuser

FROM base AS build_online

# Download a Capella executable archive
# https://github.com/moby/moby/issues/26533#issuecomment-246966836
ONBUILD ARG CAPELLA_VERSION="5.2.0"
ONBUILD ARG BUILD_ARCHITECTURE="amd64"
ONBUILD ARG CAPELLA_DOWNLOAD_URL
ONBUILD USER root
ONBUILD COPY ./download_archive.py /opt/.download_archive.py
ONBUILD RUN pip install --no-cache-dir requests && \
    python .download_archive.py ${CAPELLA_VERSION};

FROM base AS build_offline

# ONBUILD is required here
# https://github.com/moby/moby/issues/26533#issuecomment-246966836
ONBUILD ARG CAPELLA_VERSION="5.2.0"
ONBUILD ARG BUILD_ARCHITECTURE="amd"
ONBUILD COPY ./versions/${CAPELLA_VERSION}/${BUILD_ARCHITECTURE}/capella.* /opt/

FROM build_${BUILD_TYPE}

USER root
ARG CAPELLA_VERSION

RUN apt-get update && \
    apt-get install --no-install-recommends -y \
    libxtst6 \
    xdg-utils \
    x11-xserver-utils \
    xvfb \
    xauth \
    dbus-x11 && \
    rm -rf /var/lib/apt/lists/*;

RUN if [ -s capella.zip ]; then \
    # Install Capella using zip
    unzip capella.zip -d . && \
    rm capella.zip; \
    # Install Capella using tar.gz
    elif [ -s capella.tar.gz ]; then \
    tar -xf capella.tar.gz; \
    else \
    echo "capella.zip and capella.tar.gz are empty! Please add you custom Capella zip or tar.gz" && \
    exit 1; \
    fi && \
    rm -rf samples capella.zip capella.tar.gz

# Set Permissions
RUN chmod +x capella/capella && \
    chmod -R +x capella/jre/bin && \
    chmod -R +x capella/jre/lib && \
    chown -R techuser /opt/capella

COPY patch.sh /opt/patch.sh
RUN chmod +x /opt/patch.sh

# Install Dropins for Capella
USER techuser

COPY ./versions/${CAPELLA_VERSION}/dropins /opt/capella/dropins
ARG CAPELLA_DROPINS=""
COPY install_dropins.py /opt/install_dropins.py
COPY ./versions/${CAPELLA_VERSION}/dropins.yml /opt/dropins.yml

ARG MEMORY_LIMIT=5500m

RUN echo '-Dorg.eclipse.equinox.p2.transport.ecf.retry=15' >> /opt/capella/capella.ini && \
    echo '-Dorg.eclipse.ecf.provider.filetransfer.retrieve.readTimeout=10000' >> /opt/capella/capella.ini && \
    sed -i "s/-Xmx[^ ]*/-Xmx$MEMORY_LIMIT/g" /opt/capella/capella.ini
RUN python install_dropins.py

COPY ./versions/${CAPELLA_VERSION}/patches /opt/patches
RUN PATCH_DIR=/opt/patches /opt/patch.sh

USER root

# Eclipse settings
RUN mkdir -p /opt/capella/configuration/.settings; \
    ## Do not show WORKSPACE_SELECTION_DIALOG
    echo "SHOW_WORKSPACE_SELECTION_DIALOG=false" >> /opt/capella/configuration/.settings/org.eclipse.ui.ide.prefs; \
    # Setup workspace
    mkdir -p /workspace; \
    # Set workspace permissions
    chown -R techuser /workspace && \
    chmod -R 777 /opt/capella/configuration && \
    chmod -R 777 /opt/capella/p2/org.eclipse.equinox.p2.engine/profileRegistry && \
    chown techuser /opt /opt/capella/capella.ini && \
    mkdir -p /home/techuser/.config/gtk-3.0 && \
    echo "file:///workspace" >> ~/.config/gtk-3.0/bookmarks

RUN echo '-Dosgi.configuration.area=file:/opt/capella/configuration' >> /opt/capella/capella.ini
COPY setup/* /opt/setup/

ENV AUTOSTART_CAPELLA=1
ENV RESTART_CAPELLA=1
COPY ./autostart /home/techuser/.config/openbox/autostart

ENV ECLIPSE_INSTALLATION_PATH=/opt/capella
ENV ECLIPSE_EXECUTABLE=/opt/capella/capella

# Set memory options for the JVM (used by set_memory_flags.py)
ARG MEMORY_MAX=90%
ENV MEMORY_MAX=${MEMORY_MAX}
ARG MEMORY_MIN=70%
ENV MEMORY_MIN=${MEMORY_MIN}

COPY ./autostart /home/techuser/.config/openbox/autostart

COPY git_askpass.py /etc/git_askpass.py
RUN chmod 555 /etc/git_askpass.py

ARG BUILD_ARCHITECTURE=amd64
ADD https://github.com/krallin/tini/releases/download/v0.19.0/tini-$BUILD_ARCHITECTURE /tini
RUN chmod +x /tini

COPY startup.sh /startup.sh
ENTRYPOINT [ "/tini", "--", "/startup.sh" ]

ENV BASE_TYPE=capella

# Default display for virtual display
ENV USE_VIRTUAL_DISPLAY="1"
ENV DISPLAY=":99"
ENV DISPLAY_NAME="Capella $CAPELLA_VERSION"

USER techuser
