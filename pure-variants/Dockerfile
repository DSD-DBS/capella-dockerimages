# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

ARG BASE_IMAGE=capella/remote
ARG BUILD_TYPE=online
FROM ${BASE_IMAGE} as base

FROM base as online

FROM base as offline

FROM ${BUILD_TYPE}

USER techuser
COPY ./updateSite /tmp/pure-variants

RUN /opt/capella/capella \
    -consoleLog \
    -application org.eclipse.equinox.p2.director \
    -noSplash \
    -repository https://download.eclipse.org/releases/2020-06/ \
    -repository file:///tmp/pure-variants \
    -installIU com.ps.consul.eclipse.purevariants.capella.feature.group,com.ps.consul.eclipse.purevariants.emf.feature.mapping.feature.group,com.ps.consul.eclipse.purevariants.de.enterprise.feature.group

RUN sed -i '5 i\echo licenseServerLocation="$PURE_VARIANTS_LICENSE_SERVER" >> /workspace/.metadata/.plugins/org.eclipse.core.runtime/.settings/com.ps.consul.eclipse.ui.float.prefs' /home/techuser/.startup.sh
