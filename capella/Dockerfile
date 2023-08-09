# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

ARG BASE_IMAGE=base
ARG BUILD_TYPE=online
ARG INSTALL_OLD_GTK_VERSION=true
FROM ${BASE_IMAGE} as base

ENV DEBIAN_FRONTEND=noninteractive

SHELL ["/bin/bash", "-euo", "pipefail", "-c"]
ENV SHELL=/bin/bash

FROM base as old_gtk_true
# Install WebKit with GTK
ONBUILD COPY libs /tmp/libs
ONBUILD ARG INJECT_PACKAGES=false
ONBUILD RUN if [[ "$INJECT_PACKAGES" = "true" ]]; then \
    apt-get update && \
    # Inject old packages manually
    apt-get install -y $(find /tmp/libs -iname "*.deb"); \
    rm -rf /var/lib/apt/lists/*; \
    rm -r /tmp/libs; \
    else \
    # Download old packages from the Ubuntu focal registry
    ## Add source
    echo "deb http://de.archive.ubuntu.com/ubuntu/ focal main" >> /etc/apt/sources.list.d/focal.list; \
    ## Import the required keys
    apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 3B4FE6ACC0B21F32; \
    apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 871920D1991BC93C; \
    apt-get update; \
    ## Install the packages
    apt-get install -y \
    libjavascriptcoregtk-4.0-18=2.28.1-1 \
    libwebkit2gtk-4.0-37=2.28.1-1; \
    rm /etc/apt/sources.list.d/focal.list; \
    fi; \
    rm -rf /var/lib/apt/lists/*;

FROM base as old_gtk_false
ONBUILD COPY libs /tmp/libs
ONBUILD RUN apt-get update && \
    apt-get install -y \
    libjavascriptcoregtk-4.0-18 \
    libwebkit2gtk-4.0-37 && \
    rm -rf /var/lib/apt/lists/*;

FROM old_gtk_${INSTALL_OLD_GTK_VERSION} as base_new

WORKDIR /opt/

FROM base_new as build_online
# Download a Capella executable archive

# https://github.com/moby/moby/issues/26533#issuecomment-246966836
ONBUILD ARG CAPELLA_VERSION="5.2.0"
ONBUILD COPY ./download_archive.py /opt/.download_archive.py
ONBUILD RUN pip install --break-system-packages requests lxml && \
    python .download_archive.py ${CAPELLA_VERSION};

FROM base_new as build_offline

# ONBUILD is required here
# https://github.com/moby/moby/issues/26533#issuecomment-246966836
ONBUILD ARG CAPELLA_VERSION="5.2.0"
ONBUILD ARG BUILD_ARCHITECTURE="amd"
ONBUILD COPY ./versions/${CAPELLA_VERSION}/${BUILD_ARCHITECTURE}/capella.* /opt/


FROM build_${BUILD_TYPE}

ARG CAPELLA_VERSION

RUN apt-get update && \
    apt-get install -y \
    libxtst6 \
    xdg-utils \
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
RUN pip install --break-system-packages PyYAML && python install_dropins.py

COPY ./versions/${CAPELLA_VERSION}/patches /opt/patches
RUN PATCH_DIR=/opt/patches /opt/patch.sh

USER root

# Eclipse settings
RUN mkdir -p /opt/capella/configuration/.settings; \
    ## Do not show WORKSPACE_SELECTION_DIALOG
    echo "SHOW_WORKSPACE_SELECTION_DIALOG=false" >> /opt/capella/configuration/.settings/org.eclipse.ui.ide.prefs; \
    # Setup workspace
    mkdir /workspace; \
    ## Disable Welcome Screen
    mkdir -p /workspace/.metadata/.plugins/org.eclipse.core.runtime/.settings/org.eclipse.ui.prefs; \
    # Set workspace permissions
    chown -R techuser /workspace && \
    chown -R techuser /opt/capella/configuration && \
    chown -R techuser /opt/capella/p2/org.eclipse.equinox.p2.engine/profileRegistry && \
    chown techuser /opt /opt/capella/capella.ini

RUN echo '-Dosgi.configuration.area=file:/opt/capella/configuration' >> /opt/capella/capella.ini
COPY setup_workspace.py /opt/setup/setup_welcome_screen.py
COPY replace_env_variables.sh /opt/setup/replace_env_variables.sh

ENV AUTOSTART_CAPELLA=1
ENV RESTART_CAPELLA=1
COPY ./autostart /home/techuser/.config/openbox/autostart

ENV ECLIPSE_INSTALLATION_PATH=/opt/capella
ENV ECLIPSE_EXECUTABLE=/opt/capella/capella

COPY ./autostart /home/techuser/.config/openbox/autostart

ARG BUILD_ARCHITECTURE=amd64
ADD https://github.com/krallin/tini/releases/download/v0.19.0/tini-$BUILD_ARCHITECTURE /tini
RUN chmod +x /tini

COPY startup.sh /startup.sh
ENTRYPOINT [ "/tini", "--", "/startup.sh" ]

ENV BASE_TYPE=capella
