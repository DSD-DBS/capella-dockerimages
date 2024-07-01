<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Papyrus Base

The Papyrus base image runs [Eclipse Payprus](https://eclipse.dev/papyrus/) in
a Docker container.

## Supported versions

The image has been tested with the following versions:

- 6.4.0 (2023-03 release)

The only supported build architecture is amd64. To build and run the image on
other build architectures, use QEMU or Rosetta.

## Build it yourself

### Preparation

#### Download Papyrus

Download a Papyrus Linux binary `tar.gz` archive. You can get a release
directly from Papyrus. Visit <https://www.eclipse.org/papyrus/download.html> to
find the "Latest Released RCP".

Place the downloaded archive in the subdirectory
`papyrus/versions/$PAPYRUS_VERSION` of the present repository and ensure that
the end result is either

- `papyrus/versions/$PAPYRUS_VERSION/papyrus.tar.gz`.

where `PAPYRUS_VERSION` refers to the semantic version of Papyrus, e.g. `6.4.0`
for the 2023-03 release.

#### Optional: Customisation of the Papyrus client

To customise the Papyrus client you can

1. extract the downloaded archive,
1. apply any modifications (e.g., installation of plugins and/ or dropins) to
   it, and
1. compress the modified folder to get a `papyrus.tar.gz` again.

### Build it manually with Docker

```zsh
docker build -t papyrus/base papyrus --build-arg PAPYRUS_VERSION=$PAPYRUS_VERSION
```

If you want to configure the JVM memory options, have a look at
[Eclipse memory options](../eclipse/memory-options.md).

## Run the container

### Locally on X11 systems

If you don't need remote access, have a local X11 server running and just want
to run Papyrus locally, this may be the best option for you.

On some systems, you have to whitelist connections to the X-Server with:

```zsh
xhost +local
```

It allows all local programs to connect to your X server. You can further
restrict the access to the X server. Please read the
[documentation of `xhost`](https://man.archlinux.org/man/xhost.1) for more
details.

The container can be started with the following command. The `DISPLAY`
environment has to be passed to the container.

```zsh
docker run -d \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -e DISPLAY=$(DISPLAY) \
    papyrus/base
```

Papyrus should start after a few seconds.

### In a remote container (RDP)

Please follow the instructions on the [remote](../remote.md) page. When running
the image, add the following variables to the `docker run` command:

```zsh
    -e AUTOSTART_PAPYRUS=$AUTOSTART_PAPYRUS \
    -e RESTART_PAPYRUS=$RESTART_PAPYRUS \
```

Please replace the followings variables:

- `AUTOSTART_PAPYRUS` defines the autostart behaviour of Papyrus. When set to 1
  (default), Papyrus will be started as soon as an RDP connection has been
  established to the running container.
- `RESTART_PAPYRUS` defines the restart behaviour of Papyrus. When set to 1
  (default) and when `RESTART_PAPYRUS=1`, Papyrus will be re-started as soon as
  it has been exited (after clean quits as well as crashs).
