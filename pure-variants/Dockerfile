# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

ARG BASE_IMAGE=capella/remote
ARG BUILD_TYPE=online
FROM ${BASE_IMAGE} as base

FROM base as build_online
ONBUILD ENV REPOSITORY=https://download.eclipse.org/releases/2020-06/

FROM base as build_offline
ONBUILD ENV REPOSITORY=file:/tmp/dependencies
ONBUILD COPY ./dependencies /tmp/dependencies

FROM build_${BUILD_TYPE}

USER root

COPY ./updateSite /tmp/updateSite
RUN mkdir /tmp/pure-variants && \
    unzip /tmp/updateSite/* -d /tmp/pure-variants && \
    rm -rf /tmp/updateSite
COPY setup_workspace_purevariants.py /opt/setup/setup_workspace_purevariants.py

RUN /opt/capella/capella \
    -consoleLog \
    -application org.eclipse.equinox.p2.director \
    -noSplash \
    -repository ${REPOSITORY} \
    -repository file:///tmp/pure-variants \
    -installIU com.ps.consul.eclipse.purevariants.capella.feature.group,com.ps.consul.eclipse.purevariants.emf.feature.mapping.feature.group,com.ps.consul.eclipse.purevariants.de.enterprise.feature.group && \
    rm -rf /tmp/pure-variants
RUN chown -R techuser /opt/capella/plugins

USER techuser
