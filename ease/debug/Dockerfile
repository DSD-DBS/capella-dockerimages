ARG BASE_IMAGE=capella/ease/remote
FROM $BASE_IMAGE

USER root

RUN apt-get update && apt-get install -y wget

# Install Codium
RUN wget -qO - https://gitlab.com/paulcarroty/vscodium-deb-rpm-repo/raw/master/pub.gpg \
    | gpg --dearmor \
    | dd of=/usr/share/keyrings/vscodium-archive-keyring.gpg
RUN echo 'deb [ signed-by=/usr/share/keyrings/vscodium-archive-keyring.gpg ] https://download.vscodium.com/debs vscodium main' \
    | tee /etc/apt/sources.list.d/vscodium.list
RUN apt-get update && apt install -y codium