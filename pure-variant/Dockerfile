# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

ARG BASE_IMAGE=capella/base

FROM $BASE_IMAGE

ENV ECLIPSE_REPOSITORY=https://download.eclipse.org/releases/2020-06/
ENV WORKDIR=/home/techuser
ENV PURE_VARIANTS_REPOSITORY=${WORKDIR}/update-site

USER techuser

COPY update-site ${PURE_VARIANTS_REPOSITORY}

# Use Virtual Display
ENV DISPLAY :99

RUN /opt/capella/capella \
    -consoleLog \
    -application org.eclipse.equinox.p2.director \
    -noSplash \
    -repository https://download.eclipse.org/releases/2020-06/ \
    -repository file:/${PURE_VARIANTS_REPOSITORY} \
    -installIU com.ps.consul.eclipse.purevariants.capella.feature.group,com.ps.consul.eclipse.purevariants.emf.feature.mapping.feature.group,com.ps.consul.eclipse.purevariants.de.enterprise.feature.group

USER root
WORKDIR /home/techuser

COPY startup.sh /opt/startup.sh
RUN chmod +x /opt/startup.sh
ENTRYPOINT [ "/opt/startup.sh" ]
