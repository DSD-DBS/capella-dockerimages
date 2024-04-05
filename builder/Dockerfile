# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

FROM python:3.11-bookworm


SHELL ["/bin/bash", "-euo", "pipefail", "-c"]
ENV SHELL=/bin/bash

RUN apt-get update && \
    apt-get install -y maven

RUN pip install --break-system-packages --no-cache-dir lxml==4.9.3

COPY inject_architecture_into_pom.py /opt/inject_architecture_into_pom.py
COPY build_capella_from_source.sh /opt/build_capella_from_source.sh

RUN chmod +x /opt/build_capella_from_source.sh

ENTRYPOINT [ "/opt/build_capella_from_source.sh" ]
