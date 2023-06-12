<!--
 ~ SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Eclipse base

<!-- prettier-ignore -->
!!! info
    The Docker image name for this image is `eclipse/base`

The Eclipse base image runs the [Eclipse Project](https://download.eclipse.org/eclipse/downloads/)
in a Docker container. The Eclipse client can be downloaded and can optionally be customised
prior to building the Docker image.

## Supported versions

The image has been tested with the following versions:

- 4.26.0
- 4.27.0

## Supported architectures

We support and have tested the image against the `arm64` and `amd64`
build architectures for the supported versions.

## Use the prebuilt image

The Eclipse image is not available as prebuilt image yet.

## Build it yourself

### Preparation

#### Download Eclipse

Download a Eclipse Linux binary `tar.gz` archive. You can get a release
directly from Eclipse. Visit <https://download.eclipse.org/eclipse/downloads/>,
then find a release in the `Latest Release` section. Scroll down to "Platform Runtime Binary"
and select the package for the Linux platform with the matching build architecture.

Place the downloaded archive in the subdirectory `eclipse/versions/$ECLIPSE_VERSION/$BUILD_ARCHITECTURE` of the present
repository and ensure that the end result is either

- `eclipse/versions/$ECLIPSE_VERSION/$BUILD_ARCHITECTURE/eclipse.tar.gz`.

where `ECLIPSE_VERSION` refers to the semantic version of Eclipse, e.g. `4.27.0`.

#### Optional: Customisation of the Eclipse client

To customise the Eclipse client you can

1. extract the downloaded archive,
1. apply any modifications (e.g., installation of plugins and/ or dropins) to it, and
1. compress the modified folder to get a `eclipse.tar.gz` again.

### Build it manually with Docker

```zsh
docker build -t eclipse/base eclipse --build-arg ECLIPSE_VERSION=$ECLIPSE_VERSION
```

## Run the container

### Locally on X11 systems

If you don't need remote access, have a local X11 server running and just want to run Eclipse locally, this may be the best option for you.

On some systems, you have to whitelist connections to the X-Server with:

```zsh
xhost +local
```

It allows all local programs to connect to your X server. You can further restrict the access to the X server. Please read the [documentation of `xhost`](https://man.archlinux.org/man/xhost.1) for more details.

The container can be started with the following command. The `DISPLAY` environment has to be passed to the container.

```zsh
docker run -d \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -e DISPLAY=$(DISPLAY) \
    eclipse/base
```

Eclipse should start after a few seconds.

### In a remote container (RDP)

Please follow the instructions on the [remote](../remote.md) page. When running the image, add the following variables to the `docker run` command:

```zsh
    -e AUTOSTART_ECLIPSE=$AUTOSTART_ECLIPSE \
    -e RESTART_ECLIPSE=$RESTART_ECLIPSE \
```

Please replace the followings variables:

- `AUTOSTART_ECLIPSE` defines the autostart behaviour of Eclipse. When set to 1 (default), Eclipse will be started as soon
  as an RDP connection has been established to the running container.
- `RESTART_ECLIPSE` defines the restart behaviour of Eclipse. When set to 1 (default) and when `RESTART_ECLIPSE=1`,
  Eclipse will be re-started as soon as it has been exited (after clean quits as
  well as crashs).
