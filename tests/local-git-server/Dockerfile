# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

FROM alpine/git

RUN apk add --update git-daemon && \
    apk add --update lighttpd && \
    rm -rf /var/cache/apk/*

COPY lighttpd.conf /etc/lighttpd/lighttpd.conf

RUN mkdir /var/www/git; \
    mkdir /var/www/git/git-test-repo.git;

WORKDIR /var/www/git/git-test-repo.git
RUN git init -b main --bare
RUN git config --local http.receivepack true

WORKDIR /

ENTRYPOINT [ "lighttpd" ]
CMD ["-D", "-f", "/etc/lighttpd/lighttpd.conf"]
