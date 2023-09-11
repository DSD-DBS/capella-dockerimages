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

# Allow any user to start the RDP server
# Depending on the base image used, Xwrapper.config may (not) be available and has to be created.
RUN sed -i 's/allowed_users=console/allowed_users=anybody/g' /etc/X11/Xwrapper.config \
    || echo "allowed_users=anybody" > /etc/X11/Xwrapper.config && \
    chmod 666 /etc/shadow

# Set permissions
RUN mkdir -p /run/xrdp/sockdir && \
    chown -R techuser /etc/xrdp /run/xrdp /var/log/xrdp* && \
    chown techuser /var/log

WORKDIR /home/techuser

COPY startup.sh .startup.sh
RUN chmod 755 .startup.sh /home/techuser/.config/openbox/autostart

# Prepare idletime metric endpoint
RUN pip install prometheus-client

COPY metrics.py .metrics.py
RUN chown techuser /home/techuser/.metrics.py

USER techuser
ENTRYPOINT [ "/home/techuser/.startup.sh" ]
