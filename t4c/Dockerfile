# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

# syntax=docker/dockerfile:1.4

COPY setup_workspace_t4c.py /opt/setup/setup_workspace_t4c.py

RUN cat >> /layers/capella/capella/capella.ini <<EOT && chown techuser /layers/capella/capella/capella.ini
-DOBEO_LICENSE_SERVER_CONFIGURATION=\$T4C_LICENCE_SECRET
-Duser.name=\$T4C_USERNAME
-Dfr.obeo.dsl.viewpoint.collab.import.gmf.notation.keep.cdoid.as.xmiid=true
-Dfr.obeo.dsl.viewpoint.collab.import.other.elements.keep.cdoid.as.xmiid=true
EOT

COPY t4c_cli /opt/t4c_cli/t4c_cli
COPY pyproject.toml /opt/t4c_cli/pyproject.toml

WORKDIR /opt/t4c_cli
RUN pip install --no-cache-dir .

WORKDIR /opt
ENV BASE_TYPE=t4c

USER techuser

ENTRYPOINT [ "/tini", "--", "/docker_entrypoint.sh" ]
