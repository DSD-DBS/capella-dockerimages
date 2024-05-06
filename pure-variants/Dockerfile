# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

ARG BASE_IMAGE=capella/remote
FROM ${BASE_IMAGE} as base

ARG ECLIPSE_REPOSITORY=https://download.eclipse.org

SHELL ["/bin/bash", "-euo", "pipefail", "-c"]
ENV SHELL=/bin/bash

USER root

ARG PURE_VARIANTS_VERSION
ENV PURE_VARIANTS_VERSION=${PURE_VARIANTS_VERSION}

COPY ./versions/${PURE_VARIANTS_VERSION} /tmp/updateSite
RUN mkdir /tmp/pure-variants && \
    unzip /tmp/updateSite/* -d /tmp/pure-variants && \
    rm -rf /tmp/updateSite

USER techuser

RUN installUI=com.ps.consul.eclipse.purevariants.emf.feature.mapping.feature.group,com.ps.consul.eclipse.purevariants.de.enterprise.feature.group; \
    if [ "$BASE_TYPE" == "capella" ]; then installUI="com.ps.consul.eclipse.purevariants.capella.feature.group,$installUI"; fi; \
    ${ECLIPSE_EXECUTABLE:?} \
    -consoleLog \
    -application org.eclipse.equinox.p2.director \
    -noSplash \
    -repository ${ECLIPSE_REPOSITORY}/releases/2020-06/ \
    -repository file:///tmp/pure-variants \
    -installIU "$installUI"

USER root
RUN if [ "$BASE_TYPE" == "capella" ]; \
    then chmod +x ${ECLIPSE_INSTALLATION_PATH:?}/plugins/com.ps.consul.eclipse.core.linux_*/server/bin/variantsd && \
    chmod +x ${ECLIPSE_INSTALLATION_PATH:?}/plugins/com.ps.consul.eclipse.core.linux_*/server/bin/finishInstallation.sh; \
    fi; \
    rm -rf /tmp/pure-variants;

COPY setup_workspace_purevariants.py /opt/setup/setup_workspace_purevariants.py

# In some cases, the pure::variants server could not start with the error message:
# Cannot run program `...`, failed to exec spawn helper, exit value: 1
# This fixes the error by switching to the vfork launch mechanism
RUN echo '-Djdk.lang.Process.launchMechanism=vfork' >> "${ECLIPSE_EXECUTABLE:?}.ini"

USER techuser
