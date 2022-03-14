ARG BASE_IMAGE=t4c/client/base
FROM $BASE_IMAGE

USER root

RUN apt-get update && \
    apt-get install -y git-lfs xvfb && \
    rm -rf /var/lib/apt/lists/*

ARG GIT_EMAIL=contact@example.com
ARG GIT_USERNAME=CCM-Bot

COPY git_askpass.py /etc/git_askpass.py
ENV GIT_ASKPASS=/etc/git_askpass.py
RUN chmod +x /etc/git_askpass.py

COPY importer.sh /opt/capella/importer.sh
RUN chmod +x /opt/capella/importer.sh
COPY importer.sh /opt/capella/backup.sh
RUN chmod +x /opt/capella/backup.sh

ENV DISPLAY :99

WORKDIR /opt/capella

COPY startup.sh /opt/capella/startup.sh
RUN chmod +x /opt/capella/startup.sh
ENTRYPOINT [ "/opt/capella/startup.sh" ]