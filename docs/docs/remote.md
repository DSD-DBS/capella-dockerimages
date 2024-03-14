<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Remote image

The remote images allow to extend the

- Capella base image (`capella/base`)
- T4C base image (`t4c/client/base`)
- Pure::variants image (`t4c/client/pure-variants`)

with a RDP or XPRA server and a metrics endpoint to measure the container
activity.

It is a basic Linux server with a [Openbox](http://openbox.org/) installation.

## Build it yourself

### Preparation

#### Optional: Customize Openbox

!!! info "Openbox is only used for the connection method RDP."

Feel free to adjust the configurations `remote/rc.xml` and `remote/menu.xml` to
satisfy custom Openbox configuration needs.

If you like to use your own wallpaper, replace `remote/wallpaper.png`.

### Build it manually with Docker

```zsh
docker build -t $BASE_IMAGE/remote remote --build-arg BASE_IMAGE=$BASE_IMAGE
```

where `$BASE_IMAGE` is `capella/base`, `t4c/client/base` or
`t4c/client/pure-variants` (depends on the image you'd like to extend with
remote functionality)

## Run the container

Replace the followings variables:

- `$BASE_IMAGE` with `capella/base`, `t4c/client/base` or
  `t4c/client/pure-variants`. Please check the individual section
  `In a remote container (RDP)` of the individual base image documentation
  pages for additional configuration options.
- `$RMT_PASSWORD` is the password for remote connections (for the login via
  RDP) and has to be at least 8 characters long.

=== "Connect via RDP"

    The container image contains a `xrdp` server. To use RDP to connect to the container, run the container with the following command:

    ```zsh
    docker run -d \
        -p $RDP_EXTERNAL_PORT:3389 \
        -e CONNECTION_METHOD=xrdp \
        -e RMT_PASSWORD=$RMT_PASSWORD \
        $BASE_IMAGE/remote
    ```

    Replace `$RDP_EXTERNAL_PORT` with the external port that the RDP
    server should listen on (usually `3389`).

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

    The container image contains a `xpra-html5` server. To use XPRA via HTML5 to connect to the container, run the container with the following command:

    ```zsh
    docker run -d \
        -p $XPRA_PORT:10000 \
        -e CONNECTION_METHOD=xpra \
        -e RMT_PASSWORD=$RMT_PASSWORD \
        -e XPRA_SUBPATH="/" \
        $BASE_IMAGE/remote
    ```

    !!! note "Authentication"

        The mentioned command uses a cookie-based authentication method. You have to pass a cookie with the key `token` and the value `$RMT_PASSWORD`.
        To set the cookie manually, you can use browser extensions like [EditThisCookie](https://github.com/ETCExtensions/Edit-This-Cookie).

        If you want to disable authentication for local development, you can expose the container internal port 10001 instead of port 10000.
        Note that other flags like `XPRA_SUBPATH` won't work in this case.

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
