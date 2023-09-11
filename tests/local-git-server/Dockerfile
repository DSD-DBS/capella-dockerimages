# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

ARG BASE_IMAGE=debian:bookworm-slim
FROM $BASE_IMAGE

EXPOSE 80

USER root

RUN apt-get update && \
    apt-get upgrade --yes && \
    apt-get install --yes \
    git \
    lighttpd && \
    rm -rf /var/lib/apt/lists/*

COPY lighttpd.conf /etc/lighttpd/lighttpd.conf

RUN mkdir -p /var/www/git/git-test-repo.git

WORKDIR /var/www/git/git-test-repo.git
RUN git init -b main --bare
RUN git config --local http.receivepack true

WORKDIR /

ENTRYPOINT ["lighttpd", "-D", "-f", "/etc/lighttpd/lighttpd.conf"]
