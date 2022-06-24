FROM dbb-set-docker-stage-dev-local.bahnhub.tech.rz.db.de/t4c/client/ease/debug

USER root

ENV http_proxy=
ENV https_proxy=

# Development environment {{{
RUN apt-get update && apt-get install --yes curl gdb htop vim vim-nox zsh

COPY requirements.txt /tmp/requirements.txt

ADD .oh-my-zsh.tar.bz2 /root
ADD --chown=techuser:techuser .oh-my-zsh.tar.bz2 /home/techuser

COPY .p10k.zsh /root/.p10k.zsh
COPY --chown=techuser:techuser .p10k.zsh /home/techuser/.p10k.zsh

COPY .zshrc /root/.zshrc
COPY --chown=techuser:techuser .zshrc /home/techuser/.zshrc

ADD fonts.tar.bz2 /usr/local/share
RUN chmod -R 644 /usr/local/share/fonts

ADD nvim-config.tar.bz2 /root/.config
ADD --chown=techuser:techuser nvim-config.tar.bz2 /home/techuser/.config

RUN TEMP_DEB="$(mktemp)" && \
    wget -O "$TEMP_DEB" 'https://github.com/neovim/neovim/releases/download/v0.7.0/nvim-linux64.deb' && \
    dpkg -i "$TEMP_DEB" && \
    rm -f "$TEMP_DEB" && \
    # to ensure minimum setup in $HOME/.local/share/nvim:
    nvim --headless --cmd q && \
    mkdir -p /root/.local/share/nvim/site/pack/packer/start


RUN git clone --depth 1 https://github.com/wbthomason/packer.nvim \
    /root/.local/share/nvim/site/pack/packer/start/packer.nvim && \
    rm -rf /root/.local/share/nvim/site/pack/packer/start/packer.nvim/.git

# COPY packer.nvim /root/.local/share/nvim/site/pack/packer/start/packer.nvim
RUN cp -r /root/.local/share/nvim /home/techuser/.local/share && \
    ln -s /usr/bin/python3 /usr/local/bin/python3

# FZF (Fuzzy finder) {{{
RUN git clone --depth 1 https://github.com/junegunn/fzf.git /opt/fzf && \
    rm -rf /opt/fzf/.git && \
    /opt/fzf/install --all && \
    ln -s /opt/fzf/bin/fzf /usr/local/bin

# Latest Node.js and npm (needed for some language servers/ linters):
RUN curl -sL https://deb.nodesource.com/setup_17.x | bash - && \
    apt-get install --yes \
    aptitude \
    nodejs && \
    npm update -g npm

# language servers/ linters:
RUN npm install -g \
    diagnostic-languageserver \
    markdownlint-cli \
    prettier \
    vscode-json-languageserver \
    yaml-language-server;

# gitstatusd (to avoid auto-fetch by p10):
RUN mkdir -p /root/.cache/gitstatus && \
    mkdir -p /home/techuser/.cache/gitstatus

ADD gitstatusd-linux-x86_64_v1.5.4.tar.gz /root/.cache/gitstatus
ADD --chown=techuser:techuser gitstatusd-linux-x86_64_v1.5.4.tar.gz /home/techuser/.cache/gitstatus

# tree-sitter:
RUN curl -sL \
    https://github.com/tree-sitter/tree-sitter/releases/download/v0.20.6/tree-sitter-linux-x64.gz \
    -o /tmp/tree-sitter-linux-x64.gz && \
    gunzip /tmp/tree-sitter-linux-x64.gz && \
    mv /tmp/tree-sitter-linux-x64 /opt/tree-sitter && \
    chmod 755 /opt/tree-sitter && \
    ln -s /opt/tree-sitter /usr/local/bin

# Python setup for development:
RUN pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt && \
    rm /tmp/requirements.txt && \
    python3 -m pip install --upgrade pip

# }}}

# RUN apt-get update && \
#     apt-get uninstall -y \
#     libjavascriptcoregtk-4.0-18=2.28.1-1 \
#     libwebkit2gtk-4.0-37=2.28.1-1

RUN nvim --headless -c 'autocmd User PackerComplete quitall' -c 'PackerSync' && \
    nvim --headless +"sleep 2" +"TSInstall! bash c cpp css dockerfile html java javascript json lua python rst scss toml typescript" +"sleep 10" +qa && \
    nvim --headless +"sleep 2" +"VimspectorInstall!" +"sleep 30" +qa

RUN chown -R techuser:techuser /home/techuser

USER techuser

RUN nvim --headless -c 'autocmd User PackerComplete quitall' -c 'PackerSync' && \
    nvim --headless +"sleep 2" +"TSInstall! bash c cpp css dockerfile html java javascript json lua python rst scss toml typescript" +"sleep 10" +qa && \
    nvim --headless +"sleep 2" +"VimspectorInstall!" +"sleep 30" +qa
