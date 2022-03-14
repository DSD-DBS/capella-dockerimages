ARG BASE_IMAGE=t4c/client/base
FROM $BASE_IMAGE

USER root

RUN apt-get update && \
    apt-get install -y git-lfs && \
    rm -rf /var/lib/apt/lists/*

ARG GIT_EMAIL=contact@example.com
ARG GIT_USERNAME=CCM-Bot

COPY git_askpass.py /etc/git_askpass.py
ENV GIT_ASKPASS=/etc/git_askpass.py
RUN chmod +x /etc/git_askpass.py

WORKDIR /opt/capella

COPY startup.sh /opt/startup.sh
RUN chmod +x /opt/startup.sh
ENTRYPOINT [ "/opt/startup.sh" ]