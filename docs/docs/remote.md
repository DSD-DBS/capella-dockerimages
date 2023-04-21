<!--
 ~ SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Remote image

The remote images allow to extend the

- Capella base image (`capella/base`)
- T4C base image (`t4c/client/base`)
- Pure::variants image (`t4c/client/pure-variants`)

with a RDP server and a metrics endpoint to measure the container activity.

It is a basic Linux server with a [Openbox](http://openbox.org/) installation.

## Build it yourself

### Preparation

#### Optional: Customize Openbox

Feel free to adjust the configurations `remote/rc.xml` and `remote/menu.xml` to satisfy
custom Openbox configuration needs.

If you like to use your own wallpaper, replace `remote/wallpaper.png`.

### Build it manually with Docker

```zsh
docker build -t $BASE_IMAGE/remote remote --build-arg BASE_IMAGE=$BASE_IMAGE
```

where `$BASE_IMAGE` is `capella/base`, `t4c/client/base` or `t4c/client/pure-variants` (depends on the image you'd like to extend with remote functionality)

## Run the container

```zsh
docker run -d \
    -p $RDP_EXTERNAL_PORT:3389 \
    -e RMT_PASSWORD=$RMT_PASSWORD \
    $BASE_IMAGE/remote
```

Replace the followings variables:

- `$BASE_IMAGE` with `capella/base`, `t4c/client/base` or `t4c/client/pure-variants`. Please check the `In a remote container (RDP)` on the individual page of the base image for additional configuration options.
- `$RDP_EXTERNAL_PORT` to the external port for RDP on your host (usually `3389`)
- `$RMT_PASSWORD` is the password for remote connections (for the login via RDP) and has
  to be at least 8 characters long.

After starting the container, you should be able to connect to
`localhost:$RDP_EXTERNAL_PORT` with your preferred RDP Client.

For the login use the followings credentials:

- **Username**: `techuser`
- **Password**: `$RMT_PASSWORD`

The screen size is set every time the connection is established. Depending on your
RDP client, you will also be able to set the preferred screen size in the settings.

By default, Remmina (RDP client for Linux) starts in a tiny window. To fix that, you can
easily set "Use client resolution" instead of "Use initial window size" in the remote
connection profile.
