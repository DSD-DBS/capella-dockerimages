# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

ARG BUILD_TYPE=offline
ARG BASE_IMAGE=capella/base

FROM $BASE_IMAGE as prebuild

SHELL ["/bin/bash", "-euo", "pipefail", "-c"]
ENV SHELL=/bin/bash

# Somehow OpenJDK does not install in one shot due to a (cyclic?) dependency on
# package ca-certificates-java. Performing the install again fixes it.
RUN apt-get update && \
    # https://forums.debian.net/viewtopic.php?t=151997
    apt-get install -y openjdk-17-jre || apt-get install -y openjdk-17-jre && \
    rm -rf /var/lib/apt/lists/*

ARG GIT_EMAIL=contact@example.com
ARG GIT_USERNAME=CCM-Bot

RUN git config --global user.name $GIT_USERNAME && \
    git config --global user.email $GIT_EMAIL

# Use Virtual Display
ENV DISPLAY :99

RUN pip install py4j

# Offline build (fixed version)
FROM prebuild as build_offline
ONBUILD COPY extensions /tmp/extensions
ONBUILD ENV PY4J_REPOSITORY=file:/tmp/extensions/py4j
ONBUILD ENV EASE_REPOSITORY=file:/tmp/extensions/ease
ONBUILD ENV SWTBOT_REPOSITORY=file:/tmp/extensions/swtbot

# Online build (latest version)
FROM prebuild as build_online
ONBUILD ENV PY4J_REPOSITORY=https://eclipse.py4j.org/
ONBUILD ENV EASE_REPOSITORY=https://download.eclipse.org/ease/release/latest/
ONBUILD ENV SWTBOT_REPOSITORY=https://download.eclipse.org/technology/swtbot/releases/latest/

FROM build_${BUILD_TYPE}

USER techuser

# Install EASE Dependencies
# - org.py4j.feature.feature.group
RUN /opt/capella/capella \
    -consoleLog \
    -application org.eclipse.equinox.p2.director \
    -noSplash \
    -repository ${PY4J_REPOSITORY} \
    -installIU org.py4j.feature.feature.group

# Install EASE
# Following Plugins will be installed:
# - EASE Core Framework (Incubation)            org.eclipse.ease.feature.feature.group                       Eclipse.org
# - EASE UI Components (Incubation)             org.eclipse.ease.ui.feature.feature.group                    Eclipse.org
# - EASE Py4J Support (Incubation)              org.eclipse.ease.lang.python.py4j.feature.feature.group      Eclipse.org
# - EASE Python Support (Incubation)            org.eclipse.ease.lang.python.feature.feature.group           Eclipse.org
# - EASE Git Feature (Incubation)               org.eclipse.ease.modules.team.git.feature.feature.group      Eclipse.org
# - EASE Modules (Incubation)                   org.eclipse.ease.modules.feature.feature.group               Eclipse.org
RUN /opt/capella/capella \
    -consoleLog \
    -application org.eclipse.equinox.p2.director \
    -noSplash \
    -repository ${EASE_REPOSITORY} \
    -installIU org.eclipse.ease.feature.feature.group,org.eclipse.ease.ui.feature.feature.group,org.eclipse.ease.lang.python.py4j.feature.feature.group,org.eclipse.ease.lang.python.feature.feature.group,org.eclipse.ease.modules.team.git.feature.feature.group,org.eclipse.ease.modules.feature.feature.group

# Install SWTBot
# Following Plugins will be installed:
# - SWTBot for Eclipse Forms Testing            org.eclipse.swtbot.forms.feature.group                  Eclipse.org - SWTBot
# - SWTBot for Eclipse Testing                  org.eclipse.swtbot.eclipse.feature.group                Eclipse.org - SWTBot
# - SWTBot for GEF Testing                      org.eclipse.swtbot.eclipse.gef.feature.group            Eclipse.org - SWTBot
# - SWTBot for SWT Testing                      org.eclipse.swtbot.feature.group                        Eclipse.org - SWTBot
# - SWTBot IDE Features                         org.eclipse.swtbot.ide.feature.group                    Eclipse.org - SWTBot
# - SWTBot Test Recorder and Code Generator     org.eclipse.swtbot.generator.feature.feature.group      Eclipse.org - SWTBot
RUN /opt/capella/capella \
    -consoleLog \
    -application org.eclipse.equinox.p2.director \
    -noSplash \
    -repository ${SWTBOT_REPOSITORY} \
    -installIU org.eclipse.swtbot.forms.feature.group,org.eclipse.swtbot.eclipse.feature.group,org.eclipse.swtbot.eclipse.gef.feature.group,org.eclipse.swtbot.feature.group,org.eclipse.swtbot.ide.feature.group,org.eclipse.swtbot.generator.feature.feature.group

USER root

RUN rm -rf /tmp/extensions
RUN echo "-Dorg.eclipse.swtbot.search.timeout=1000" >> /opt/capella/capella.ini

RUN pip install pyease

ENV EASE_WORKSPACE /workspace
ENV EASE_SCRIPTS_LOCATION /opt/scripts
ENV EASE_LOG_LOCATION=/proc/1/fd/1

RUN mkdir /opt/scripts && \
    chown techuser /opt/scripts

# Clean Workspace and set it up for EASE
RUN python -m pyease.ease
RUN chown -R techuser /workspace

WORKDIR /home/techuser

COPY git_askpass.py /etc/git_askpass.py
ENV GIT_ASKPASS=/etc/git_askpass.py
RUN chmod +rx /etc/git_askpass.py

COPY startup.sh /opt/startup.sh
RUN chmod +x /opt/startup.sh
ENTRYPOINT [ "/opt/startup.sh" ]
