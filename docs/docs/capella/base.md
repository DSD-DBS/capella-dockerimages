<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Capella base

<!-- prettier-ignore -->
!!! info
    The Docker image name for this image is `capella/base`

The Capella base image installs a selected Capella client version. The Capella
client can be downloaded and can optionally be customised prior to building the
Docker image or can be downloaded automatically in the Docker image.

The images are meant to have a containerised Capella (with or without a Team
for Capella client) that can be run headless (as command line interface).

<!-- prettier-ignore -->
!!! info
    The functionality for running capella as a command-line app used to be part of
    the `capella/cli` image. An image with this name is no longer built. Use
    `capella/base` instead.

## Use the prebuilt image

```
docker run ghcr.io/dsd-dbs/capella-dockerimages/capella/base:$TAG
```

where `$TAG` is the Docker tag. For more information, have a look at our
[tagging schema](introduction.md#tagging-schema-for-prebuilt-images).

Please check the [`Run the container`](#run-the-container) section for more
information about the usage.

## Build it yourself

### Preparation

#### Optional: Download Capella manually

Download a Capella Linux binary `zip` or `tar.gz` archive. You can get a
release directly from Eclipse. Visit
<https://github.com/eclipse/capella/releases>, select a version and follow the
hyperlink labelled `Product` to find a binary release for Linux.

Place the downloaded archive in the subdirectory
`capella/versions/$CAPELLA_VERSION/$ARCHITECTURE` of the present repository and
ensure that the end result is either

- `capella/versions/$CAPELLA_VERSION/$ARCHITECTURE/capella.tar.gz` or
- `capella/versions/$CAPELLA_VERSION/$ARCHITECTURE/capella.zip`.

Check that the archive has a structure similar to the following coming with a
top level directory named `capella` and several sub directories and files in
it.

For Capella 5.0.0 the structure is illustrated below:

```zsh
$ tree -L 1 capella
capella
├── artifacts.xml
├── capella
├── capella.ini
├── configuration
├── dropins
├── epl-v10.html
├── features
├── jre
├── notice.html
├── p2
├── plugins
└── readme
```

#### Optional: Customisation of the Capella client

To customise the Capella client you can

1. extract the downloaded archive,
1. apply any modifications (e.g., installation of plugins and/ or dropins) to
   it, and
1. compress the modified folder `capella` to get a `capella.zip` or
   `capella.tar.gz` again.

##### Install dropins

As alternative to the solution presented above, we provide an interface to
install dropins.

You have to pass a comma-separated list of dropin names as `CAPELLA_DROPINS`
build argument to the `docker build` command:

```zsh
--build-arg CAPELLA_DROPINS="ModelsImporter,CapellaXHTMLDocGen,DiagramStyler,PVMT,Filtering,Requirements,SubsystemTransition"
```

Supported dropins are:

- [CapellaXHTMLDocGen](https://github.com/eclipse/capella-xhtml-docgen)
- [DiagramStyler](https://github.com/eclipse/capella/wiki/PVMT)
- [PVMT](https://github.com/eclipse/capella/wiki/PVMT)
- [Filtering](https://github.com/eclipse/capella-filtering)
- [Requirements](https://github.com/eclipse/capella-requirements-vp)
- [SubsystemTransition](https://github.com/eclipse/capella-sss-transition)
- [TextualEditor](https://github.com/eclipse/capella-textual-editor)

The dropins are registered in the
`capella/versions/$CAPELLA_VERSION/dropins.yml` file. If you're missing a
dropin in the list, feel free to open a PR.

#### Optional: Workaround of pinned library versions to remove incompatibilities

**Note:** _This workaround is normally handled in the Dockerfile and it is only
necessary to download below libraries if there are restrictions on your network
that block an access to these libraries when the Docker image is being built._

In some Capella versions, there are incompatiblities with certain versions of
the following libraries:

- `libjavascriptcoregtk-4.0-18` (version `2.32.4`)
- `libwebkit2gtk-4.0-37` (version `2.32.4`)

The workaround is to use version `2.28.1` for both libraries in the container.

So if your build environment restricts access to the latest versions you need
to manually download the packages with the command `apt download` and inject
them into the container.

For more information refer to
[Download older packages manually](#download-older-packages-manually).

<!-- prettier-ignore -->
!!! info
    You have to add `--build-arg INJECT_PACKAGES=true` to the `docker build` command if you want to use the previously downloaded packages.

### Build it manually with Docker

If you want to download the Capella archive automatically, use the following
command. Does only work for
[supported Capella versions](introduction.md#supported-versions).

```zsh
docker build -t capella/base capella --build-arg BUILD_TYPE=online --build-arg CAPELLA_VERSION=$CAPELLA_VERSION
```

If you've downloaded the Capella archive manually before, use this command:

```zsh
docker build -t capella/base capella --build-arg CAPELLA_VERSION=$CAPELLA_VERSION
```

### Miscellaneous

#### Download older debian packages manually

Unfortunately the version `2.28.1` of `libwebkit2gtk-4.0-37` is no longer
available in the stable Debian registry, but it is still available in the
Ubuntu `focal` repository
(<https://packages.ubuntu.com/focal/libwebkit2gtk-4.0-37>).

First of all, you have to add the source to your `apt`-sources and add the apt
keys.

Recommendation: Spawn a `debian:bookworm` Docker container and execute the
steps inside the container.

```zsh
apt update && apt install -y gnupg
echo "deb http://security.ubuntu.com/ubuntu focal-security main" >> /etc/apt/sources.list.d/focal.list
apt-key adv --keyserver keyserver.ubuntu.com --recv-keys "3B4FE6ACC0B21F32"
apt-key adv --keyserver keyserver.ubuntu.com --recv-keys "871920D1991BC93C"
apt update
```

Please download all packages and place the files in the folder `capella/libs`:

- `libicu66_66.1-2ubuntu2_amd64.deb` <br /> (Run
  `apt download libicu66=66.1-2ubuntu2`)

- `libjavascriptcoregtk-4.0-18_2.28.1-1_amd64.deb` <br /> (Run
  `apt download libjavascriptcoregtk-4.0-18=2.28.1-1`)

- `libjpeg-turbo8_2.0.3-0ubuntu1_amd64.deb` <br /> (Run
  `apt download libjpeg-turbo8=2.0.3-0ubuntu1`)

- `libjpeg8_8c-2ubuntu8_amd64.deb` <br /> (Run
  `apt download libjpeg8=8c-2ubuntu8`)

- `libwebkit2gtk-4.0-37_2.28.1-1_amd64.deb` <br /> (Run
  `apt download libwebkit2gtk-4.0-37=2.28.1-1`)

- `libwebp6_0.6.1-2ubuntu0.20.04.2_amd64.deb` <br /> (Run
  `apt download libwebp6=0.6.1-2ubuntu0.20.04.2`)

## Run the container

### Locally on X11 systems

If you don't need remote access, have a local X11 server running and just want
to run Capella locally, this may be the best option for you.

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
    capella/base
```

Capella should start after a few seconds.

### In a remote container (RDP)

Please follow the instructions on the [remote](../remote.md) page. When running
the image, add the following variables to the `docker run` command:

```zsh
    -e AUTOSTART_CAPELLA=$AUTOSTART_CAPELLA \
    -e RESTART_CAPELLA=$RESTART_CAPELLA \
```

Please replace the followings variables:

- `AUTOSTART_CAPELLA` defines the autostart behaviour of Capella. When set to 1
  (default), Capella will be started as soon as an RDP connection has been
  established to the running container.
- `RESTART_CAPELLA` defines the restart behaviour of Capella. When set to 1
  (default) and when `AUTOSTART_CAPELLA=1`, Capella will be re-started as soon
  as it has been exited (after clean quits as well as crashs).

### Example to export representations (diagrams) as SVG images

Replace `/path/to/model` and `<PROJECT_NAME>` to pass any local Capella model.
Set the project name so that it fits your Capella project name for the model as
it is given in the file `/path/to/model/.project`.

Exported diagrams will appear on the host machine at `/path/to/model/diagrams`.

```zsh
docker run --rm -it \
  -v /path/to/model:/model \
  capella/base \
  -nosplash \
  -consolelog \
  -application org.polarsys.capella.core.commandline.core \
  -appid org.polarsys.capella.exportRepresentations \
  -data /workspace \
  -import /model \
  -input "/all" \
  -imageFormat SVG \
  -exportDecorations \
  -outputfolder /<PROJECT_NAME>/diagrams \
  -forceoutputfoldercreation
```
