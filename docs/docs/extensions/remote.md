<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Remote extension

!!! info ""

    This extension in only available when using `capella`, `eclipse` or `papyrus` as base.

This extension embeds an RDP and Xpra server and a metrics endpoint to measure
the container activity into the container image.

The remote extension is enabled per default. If you want to decrease the
container size, you can skip the installation during the image build:

=== "Build via `make`"

    `REMOTE_EXTENSION_ENABLED=0 make <target>`

=== "Build via `pack`"

    Pass `--env REMOTE_EXTENSION_ENABLED=0` to the `pack build` command.

## Run the container

Replace the followings variables:

=== "Connect via RDP"

    The container image contains a `xrdp` server. To use RDP to connect to the container, add the following flags to your `docker run` command:

    ```zsh
    -p $RDP_EXTERNAL_PORT:3389 \
    -e CONNECTION_METHOD=xrdp \
    -e RMT_PASSWORD=$RMT_PASSWORD
    ```

    Replace `$RDP_EXTERNAL_PORT` with the external port that the RDP
    server should listen on (usually `3389`).

    Also replace `$RMT_PASSWORD` with the password for remote connections
    (for the login via RDP). The value has to be at least 8 characters long.

    After starting the container, you should be able to connect to
    `localhost:$RDP_EXTERNAL_PORT` with your preferred RDP Client.

    For the login use the followings credentials:

    - **Username**: `techuser`
    - **Password**: `$RMT_PASSWORD`

    The screen size is set every time the connection is established. Depending on your
    RDP client, you will also be able to set the preferred screen size in the settings.

    By default, Remmina (RDP client for Linux) starts in a tiny window. To fix that, you can
    set "Use client resolution" instead of "Use initial window size" in the remote
    connection profile.

=== "Connect via XPRA"

    The container image contains a `xpra-html5` server. To use XPRA via HTML5 to connect to the container, add the following flags to your `docker run` command:

    ```zsh
    -p $XPRA_PORT:10000 \
    -e CONNECTION_METHOD=xpra \
    -e XPRA_SUBPATH="/"
    ```

    !!! warning "Authentication"

        Since version v1.19.0, xpra based containers are exposed without authentication.
        If used with the Capella Collaboration Manager >= v3.1.0, authentication is handled via session pre-authentication automatically.
        In other cases, you have to implement your own authentication mechanism.

    !!! note "Embedding in iframes"

        To embed the XPRA session in an iframe, you have to set a custom Content Security Policy. You can pass the environment variable `XPRA_CSP_ORIGIN_HOST`
        to the hostname of the website you'd like to embed the XPRA session in. If you want to embed the XPRA session in an iframe on `example.com`, set `XPRA_CSP_ORIGIN_HOST` to `https://example.com`.

    Set the `XPRA_SUBPATH` to the subpath that `xpra` should serve on. If you want to have it running on `/xpra`, set `XPRA_SUBPATH` to `/xpra`.

    Then, open a browser and connect to:
    ```
    http://localhost:${XPRA_PORT}${XPRA_SUBPATH}/?floating_menu=0
    ```

    More configuration options can be passed as query parameters.
    See the [xpra-html5 documentation](https://github.com/Xpra-org/xpra-html5/blob/master/docs/Configuration.md)
    for more information.
