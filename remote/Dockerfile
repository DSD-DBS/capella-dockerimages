# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

ARG BASE_IMAGE=capella/base
FROM ${BASE_IMAGE}

ARG DEBIAN_FRONTEND=noninteractive

SHELL ["/bin/bash", "-euo", "pipefail", "-c"]
ENV SHELL=/bin/bash

# Install RDP (XRDP with XORG)
USER root

RUN apt-get update && apt-get upgrade -y && apt-get install -y \
    xrdp \
    xserver-xorg-core \
    xorgxrdp \
    openbox \
    obconf \
    gettext-base \
    xprintidle \
    nitrogen && rm -rf /var/lib/apt/lists/*

COPY rc.xml /etc/xdg/openbox/rc.xml
COPY menu.xml /etc/xdg/openbox/menu.xml

# Setup Nitrogen (Desktop background)
COPY wallpaper.png /tmp/wallpaper.png
COPY bg-saved.cfg /home/techuser/.config/nitrogen/bg-saved.cfg

# Copy Supervisor Configuration
RUN pip install supervisor
COPY supervisord.conf /etc/supervisord.conf

# Allow any user to start the RDP Server
RUN sed -i 's/allowed_users=console/allowed_users=anybody/g' /etc/X11/Xwrapper.config

RUN id techuser || useradd -l -m -u 1001000000 techuser && echo "techuser:tmp_passwd" | chpasswd

# Set permissions
RUN mkdir -p /run/xrdp/sockdir && \
    chown techuser /opt /opt/capella/capella.ini && \
    chown -R techuser /etc/xrdp /run/xrdp /var/log/xrdp* && \
    chown techuser /var/log && \
    chown -R techuser /opt/capella/configuration

WORKDIR /home/techuser

COPY startup.sh .startup.sh
COPY autostart .config/openbox/autostart
RUN chmod 755 .startup.sh .config/openbox/autostart

# Prepare idletime metric endpoint
RUN pip install prometheus-client

COPY metrics.py .metrics.py

# Run fileservice endpoint
COPY fastapi /opt/fastapi
RUN pip install /opt/fastapi

ENV AUTOSTART_CAPELLA=1
ENV RESTART_CAPELLA=1

USER techuser
ENTRYPOINT [ "/home/techuser/.startup.sh" ]
