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

#### Install dropins

##### Automatic installation

The image builder can automatically download dropins for Capella and inject
them into the Capella client.

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

##### Manual installation

If you want to install dropins manually, you can place the dropins in the
`capella/versions/$CAPELLA_VERSION/dropins` directory. The dropins will be
copied into the `dropins` directory of the Capella client without any further
processing.

If you only have the updateSite and not the dropin, you can create a file `dropins.overwrites.yml` next to the `dropins.yml` in `capella/versions/$CAPELLA_VERSIONS` with the following content:

```yaml
dropins:
  NameOfTheDropin:
    type: updateSite
    eclipseRepository:
      - <filename>.zip # (1)!
      - 'https://download.eclipse.org/releases/2023-03' # (2)!
    installIU: # (3)!
      - org.eclipse.xxx.feature.feature.group
    tag: "FeaturePatch" # (4)!
    profile: "DefaultProfile" # (5)!
    autouse: false # (6)!
    proxy: null # (7)!
    disable_mirrors: false # (8)!
```

1. Place the file in the `capella/versions/$CAPELLA_VERSION/patches` directory and specify the filename here. Must be a zip file.
2. Specify additional registries like the Eclipse registry to fetch dependencies from.
3. Add all IDs of installable units that you want to install. You can see those while installing the updateSite via the Capella UI.
4. Optional tag if required. Remove the line if no tag is required.
5. Optional profile to use. Remove the line if no profile is required. If transitioning from `patch_info.csv`, use the profile `DefaultProfile`.
6. If `autouse` is enabled, the dropin will be installed independently of the `CAPELLA_DROPINS` build argument.
7. Optional proxy to fetch external registries. If not set, no proxy will be used. To use the proxy of the environment, set it to `{proxy}`.
8. Decide if mirrors should be disabled or not. This might be needed if you run your own mirror.

### Build it manually with Docker

#### Automatic download of Capella

If you want to download the Capella archive automatically, use the following
command. It does only work for
[supported Capella versions](introduction.md#supported-versions).

```zsh
docker build -t capella/base capella --build-arg BUILD_TYPE=online --build-arg CAPELLA_VERSION=$CAPELLA_VERSION
```

You can further customize the mirror to download the Capella archive from. If
you don't want to use the default mirror, choose another mirror from
[this list](https://www.eclipse.org/downloads/download.php?file=/capella/core/products/releases&format=xml).

Then, append `/{}` to the mirror URL and pass it as a build argument to the
above command, e.g.:

```zsh
--build-arg CAPELLA_DOWNLOAD_URL="https://mirror.umd.edu/eclipse/capella/core/products/releases/{}"`
```

#### Build with pre-downloaded version of Capella

If you've downloaded the Capella archive manually before, use this command:

```zsh
docker build -t capella/base capella --build-arg CAPELLA_VERSION=$CAPELLA_VERSION
```

With this method, you can customize the Capella client before running the above
command:

1. Extract the downloaded archive,
1. Apply any modifications (e.g., installation of plugins and/ or dropins) to
   it, and
1. Compress the modified folder `capella` to get a `capella.zip` or
   `capella.tar.gz` again.

### Miscellaneous

## Run the container

### Configuration Options

There are a few configuration options that can be passed to the container.

#### Semantic Browser Auto-refresh

One
[performance recommendation](https://github.com/eclipse-capella/capella/blob/master/doc/plugins/org.polarsys.capella.th.doc/html/Performance%20Recommandations/Performance%20Recommandations.mediawiki#desynchronize-semantic-browser)
of the Capella team is to disable the semantic browser auto-refresh.

The semantic browser synchronization is disabled by default in our containers.
To follow a more streamlined approach, it will also be disabled if actively
changed in the UI / workspace.

To disable this behaviour and just keep the option as it is, pass the following
flag to the `docker run` command:

```zsh
--env CAPELLA_DISABLE_SEMANTIC_BROWSER_AUTO_REFRESH=0
```

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

### In a remote container

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

If you want to configure the JVM memory options, have a look at
[Eclipse memory options](../eclipse/memory-options.md).

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
