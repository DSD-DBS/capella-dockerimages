<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Capella Base

The Capella base image installs a selected Capella client version. The Capella
client can be downloaded and can optionally be customised prior to building the
Docker image or can be downloaded automatically in the Docker image.

The images are meant to have a containerised Capella (with or without a Team
for Capella client) that can be run headless (as command line interface).

!!! info

    The functionality for running capella as a command-line app used to be part of
    the `capella/cli` image. An image with this name is no longer built. Use
    `capella/base` instead.

## Supported versions

Currently, we support Capella versions `5.0.0`, `5.2.0`, `6.0.0`, and `6.1.0`.

## Use the prebuilt image

```
docker run ghcr.io/dsd-dbs/capella-dockerimages/capella/base:$TAG
```

where `$TAG` is the Docker tag. For more information, have a look at our
[tagging schema](#tagging-schema).

Please check the [`Run the container`](#run-the-container) section for more
information about the usage.

### Tagging schema

The Capella related images are tagged using the following schema:

`$CAPELLA_VERSION-$DROPINS_TYPE-$CAPELLA_DOCKER_IMAGES_REVISION`, e.g.,
`6.0.0-selected-dropins-v1.10.2` for Capella version `6.0.0` with selected
dropins and Capella Docker images revision `v1.10.2`.

`$CAPELLA_VERSION` is the semantic version of Capella (see supported versions
[above](#supported-versions)). `$DROPINS_TYPE` is the name of the set of
dropins. `$CAPELLA_DOCKER_IMAGES_REVISION` can be a tag or branch of this
repository. In case of branches, all characters matching the regex
`[^a-zA-Z0-9.]` will be replaced with `-`.

We don't tag images with the `latest` tag. You may want to use
`$CAPELLA_VERSION-selected-dropins-main` for the latest version, but we
recommend using tags for the best stability.

### Supported dropins

Our prebuilt images are published a pre-selected set of dropins. Available
options are:

- `without-dropins`: Without dropins
- `selected-dropins`: With
  [CapellaXHTMLDocGen](https://github.com/eclipse/capella-xhtml-docgen),
  [DiagramStyler](https://github.com/eclipse/capella/wiki/PVMT),
  [PVMT](https://github.com/eclipse/capella/wiki/PVMT),
  [Filtering](https://github.com/eclipse/capella-filtering),
  [Requirements](https://github.com/eclipse/capella-requirements-vp) and
  [SubsystemTransition](https://github.com/eclipse/capella-sss-transition)

If you need a custom set of dropins, you have two options:

**Option 1**: Mount a dropins folder with all dropins into
`/opt/capella/dropins` when starting the container.

**Option 2**: Build the image manually. More information:
[Build it yourself](#build-it-yourself)

## Build it yourself

### Preparation

#### Optional: Download Capella manually

Download a Capella Linux binary `tar.gz` archive. You can get a release
directly from Eclipse. Visit <https://github.com/eclipse/capella/releases>,
select a version and follow the hyperlink labelled `Product` to find a binary
release for Linux.

Save the downloaded archive as
`capella/versions/$CAPELLA_VERSION/$ARCHITECTURE/capella.tar.gz`.

If you don't have a Capella archive, we'll download it automatically.

#### Optional: Install dropins

=== "Download automatically"

    You have to pass a comma-separated list of dropin names as `CAPELLA_DROPINS`
    build argument to the `pack build` command:

    ```zsh
    --env CAPELLA_DROPINS="ModelsImporter,CapellaXHTMLDocGen,DiagramStyler,PVMT,Filtering,Requirements,SubsystemTransition"
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

=== "Download manually"

You can also download the dropins manually and copy the dropins to the
`capella/versions/$CAPELLA_VERSION/dropins` directory. The directory structure
will be preserved.

### Build it manually

```zsh
pack build capella \
		--env TOOL=capella \
		--env CAPELLA_VERSION="$CAPELLA_VERSION" \
		--uid "$TECHUSER_UID" \
		--builder mbse-builder
```

<hr>

## Run the container

If you want to configure the JVM memory options, have a look at
[Eclipse memory options](../eclipse/memory-options.md).

### Locally on X11 systems

If you don't need remote access, have a local X11 server running and just want
to run Capella locally, this may be the best option for you.

On some systems, you have to whitelist connections to the X-Server with:

```zsh
xhost +local
```

It allows all local programs to connect to your X server. You can further
restrict the access to the X server. Please read theThis feature replaces the
read-only image
[documentation of `xhost`](https://man.archlinux.org/man/xhost.1) for more
details.

The container can be started with the following command. The `DISPLAY`
environment has to be passed to the container.

```zsh
docker run -d \
    --entrypoint capella \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v /path/to/your/local/volume:/workspace \
    -e DISPLAY=$(DISPLAY) \
    capella
```

Capella should start after a few seconds.

### Remotely

Please follow the instructions on the
[remote extension](../../extensions/remote.md) page. When running the image,
add the following variables to the `docker run` command:

```zsh
-e AUTOSTART_CAPELLA=$AUTOSTART_CAPELLA
-e RESTART_CAPELLA=$RESTART_CAPELLA
```

Please replace the followings variables:

- `AUTOSTART_CAPELLA` defines the autostart behaviour of Capella. When set to 1
  (default), Capella will be started as soon as an RDP connection has been
  established to the running container.
- `RESTART_CAPELLA` defines the restart behaviour of Capella. When set to 1
  (default) and when `AUTOSTART_CAPELLA=1`, Capella will be re-started as soon
  as it has been exited (after clean quits as well as crashs).

### Use the Capella CLI

You can use the Capella CLI directly. All arguments passed to the `docker run`
command are passed to Capella directly.

```
docker run --rm -it \
  --entrypoint capella
  capella
```

#### Example to export representations (diagrams) as SVG images

Replace `/path/to/model` and `<PROJECT_NAME>` to pass any local Capella model.
Set the project name so that it fits your Capella project name for the model as
it is given in the file `/path/to/model/.project`.

Exported diagrams will appear on the host machine at `/path/to/model/diagrams`.

```zsh
docker run --rm -it \
  --entrypoint capella \
  -v /path/to/model:/model \
  capella \
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

### Load models to your workspace automatically

!!! info "Technical prerequisites"

    The feature relies on an Eclipse plugin that is not part of Capella.
    The plugin is called `models-from-directory-importer` and is available
    on GitHub: https://github.com/DSD-DBS/capella-addons.

    The plugin is part of all Capella based pre-built images on GitHub.
    If you build it manually, make sure that you follow the ["Install dropins" instructions](./base.md#install-dropins).

To load models to your workspace automatically, you can mount a volume to the
container.

```
docker run -d \
    -v path/to/models/on/host:/models \
    -e ECLIPSE_PROJECTS_TO_LOAD='[]' \
    capella/base
```

The `ECLIPSE_PROJECTS_TO_LOAD` environment variable is a JSON array that
contains:

```json
[
  {
    "revision": "master", // (1)
    "nature": "project", // (2)
    "path": "/models/directory", // (3)
    "entrypoint": "test.aird" // (4)
  }
]
```

1. The revision of the Eclipse project. In case of duplicated project names,
   the revision is added as suffix to the project name.
2. Optional: Can be either 'project' or 'library'. Defaults to 'project'.
   Ignored if the the directory provided in the `path` attribute contains a
   `.project` file.
3. Path to the directory where the project should be loaded from.
4. Path to the aird file, starting from the directory provided in the `path`
   attribute. Required if the `.aird` is not placed directly in the directory
   provided as `path`. If None, the aird is searched in the path directory
   without recursion.

All additional attributes are ignored.

You can use all images that are based on the `capella/base` image for this
feature.
