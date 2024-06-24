# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

ARG BASE_IMAGE=capella/base
FROM ${BASE_IMAGE}

# Port if xrdp is used as connection method.
EXPOSE 3389

# Port if xpra is used as connection method.
EXPOSE 10000

ARG DEBIAN_FRONTEND=noninteractive

SHELL ["/bin/bash", "-euo", "pipefail", "-c"]
ENV SHELL=/bin/bash

# Install RDP (XRDP with XORG)
USER root

# Install xrdp and dependencies
RUN apk add --no-cache \
    xrdp \
    xorg-server \
    xorgxrdp \
    openbox \
    obconf-qt \
    gettext \
    xprintidle \
    xpra \
    xpra-webclient \
    apache2-utils \
    nginx

COPY rc.xml /etc/xdg/openbox/rc.xml
COPY menu.xml /etc/xdg/openbox/menu.xml

# Copy Supervisor Configuration
RUN pip install --no-cache-dir supervisor==4.2.5
COPY supervisord.conf /etc/supervisord.conf
COPY supervisord.*.conf /tmp/supervisord/

# Copy nginx configuration for xpra
COPY nginx.conf /etc/nginx/nginx.conf
COPY error.html /usr/share/nginx/html/error.html

# Allow any user to start the RDP server
# Depending on the base image used, Xwrapper.config may (not) be available and has to be created.
RUN sed -i 's/allowed_users=console/allowed_users=anybody/g' /etc/X11/Xwrapper.config \
    || echo "allowed_users=anybody" > /etc/X11/Xwrapper.config && \
    chmod 666 /etc/shadow

# Set permissions
RUN mkdir -p /run/xrdp/sockdir /var/log/nginx && \
    chown -R techuser /etc/xrdp /run/xrdp && \
    chown techuser /var/log && \
    chown techuser /etc/supervisord.conf /var/log/nginx && \
    chown techuser /etc/nginx && \
    touch /etc/environment && chown techuser /etc/environment

WORKDIR /home/techuser

COPY startup.sh .startup.sh
RUN chmod 755 .startup.sh /home/techuser/.config/openbox/autostart

# Prepare idletime metric endpoint
RUN pip install --no-cache-dir prometheus-client==0.17.1

COPY metrics.py .metrics.py
RUN chown techuser /home/techuser/.metrics.py

USER techuser
ENTRYPOINT [ "/home/techuser/.startup.sh" ]
