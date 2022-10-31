<!--
SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors

SPDX-License-Identifier: Apache-2.0
-->

# Capella, T4C Client and EASE Docker images

## Introduction

Please read the **complete** README carefully first, as some requirements must be met
for the containers to work as desired.

The repository provides Docker images for the followings tools:

- [Capella](https://www.eclipse.org/capella/)
- [TeamForCapella client](https://www.obeosoft.com/en/team-for-capella) \
  Right now, we don't provide a Docker image for the server.
- [EASE](https://www.eclipse.org/ease/) \
  [SWT-Bot](https://www.eclipse.org/swtbot/)

This repository includes Docker files to build the following Docker images:

| Name of the Docker image | Short description |
|------|---|
| `base` |This is the base image that has the most important tools pre-installed.|
| `capella/base`|This is the Capella base image. It is a simple container with Capella and the required dependencies installed. No more.|
| `t4c/client/base`|This extends the Capella base image with the T4C client and the dependencies.|
| `capella/ease`<br>`t4c/client/ease`|This extends the Capella or T4C client base image with EASE and SWTBot functionality. You can mount every Python script and execute it in a container environment. |
| `capella/remote`<br>`t4c/client/remote`|The remote image will add an RDP server on top of any other image. This will provide the user the possibility to connect and work inside the container.|
| `capella/readonly`|This image has capability to clone a Git repository, will load the project into the workspace and also offers RDP.|

Important for building the Docker images is to strictly follow the sequence.
The dependency graph for the images looks like:

```mermaid
flowchart LR
    A(base) --> B(capella/base)
    B(capella/base) --> C(t4c/client/base)
    B(capella/base) --> D(capella/ease)
    C(t4c/client/base) --> E(t4c/client/ease)
    B(capella/base) --> F(capella/remote)
    C(t4c/client/base) --> G(t4c/client/remote)
    D(capella/ease) --> H(capella/ease/remote) --> I(capella/readonly)
    style A fill:#ebb134
    style B fill:#8feb34
    style C fill:#34cceb
    style D fill:#eb3477
    style E fill:#eb3477
    style F fill:#f2f1a7
    style G fill:#f2f1a7
    style H fill:#f2f1a7
    style I fill:#d0a7f2
```

## Build the images

Please clone this repository and include all submodules:

```zsh
git clone --recurse-submodules https://github.com/DSD-DBS/capella-dockerimages.git
```

**Make sure that all commands are executed in the root directory of the repository.**

> :information_source: When running the build targets with `PUSH_IMAGES=1`, they get pushed to your preferred registry after each build.

### Quick Start

The Quick Start can only be used if the following conditions are met:

- Only the standard configuration is required.
- All files are already in the right place.

If the conditions are not fulfilled, please continue with the next step.

Otherwise, you can simply run the following command to build all images:

```sh
make all
```

### 1. Docker image `base`

Our base image updates the packages and installs the following packages:

- `python3`
- `python3-pip`

Also, we create a custom user `techuser`. This user will always be used to run the
containers and allows to assign a custom `UID`. This can make sense, if you want to
deploy the containers in a K8s cluster and your company has some security restrictions
(e.g. specific `UID` ranges).

Feel free to modify this image to your specific needs. You are able to set proxies,
custom registry URLs, your timezone, CA certificates and any other stuff.

To build the base image, please run:

```zsh
docker build -t base base
```

**Important:**
 If your company has a specific base image with all company configurations, of course,
 it can also be used:

```zsh
docker build -t base --build-arg BASE_IMAGE=$CUSTOM_IMAGE base
```

Make sure that your `$CUSTOM_IMAGE` is a Linux image that has the common tools installed
and uses the `apt` / `apt-get` package manager. If this is not the case, the image
cannot be used. Our images were tested with the image `debian:bullseye`.

If you like to set a custom `UID` for the user `techuser`, you can run:

```zsh
docker build -t base --build-arg UID=1001 base
```

### 2. Docker image `capella/base`

The Capella base image installs a selected Capella client version. The Capella client can be downloaded and can optionally be customised prior to building the Docker
image or can be downloaded automatically in the Docker image.

#### Option 1: Download Capella archive manually

Download a Capella Linux binary `zip` or `tar.gz` archive. You can get a release
directly from Eclipse. Visit <https://github.com/eclipse/capella/releases>, select a
version and follow the hyperlink labelled `Product` to find a binary release for Linux.

Place the downloaded archive in the subdirectory `capella/archives` of the present
repository and ensure that the end result is either

- `capella/archives/capella.tar.gz` or
- `capella/archives/capella.zip`.

Check that the archive has a structure similar to the following coming with a top level
directory named `capella` and several sub directories and files in it.

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

#### Optional: customisation of the Capella client

To customise the Capella client you can

1. extract the downloaded archive,
1. apply any modifications (e. g. installation of plugins and/ or dropins) to it, and
1. compress the modified folder `capella` to get a `capella.zip` or `capella.tar.gz`

again.

#### Workaround of pinned library versions to remove incompatibilities

**Note:** \
_This workaround is normally handled in the [Dockerfile](capella/Dockerfile) and it is
only necessary to download below libraries if there are restrictions on your network
that block an access to these libraries when the Docker image is being built._

In some Capella versions, there are incompatiblities with certain versions of the
following libraries:

- `libjavascriptcoregtk-4.0-18` (version `2.32.4`)
- `libwebkit2gtk-4.0-37` (version `2.32.4`)

The workaround is to use version `2.28.1` for both libraries in the container.

So if your build environment restricts access to the latest versions you need to
manually download the packages with the command `apt download` and inject them into the
container.

For more information refer to [Download older packages manually](#download-older-packages-manually).

#### Build the Docker image

If you skipped the previous workaround, execute the following command:

```zsh
docker build -t capella/base capella
```

If you applied the previous workaround and manually downloaded the older libraries, use
the following command:

```zsh
docker build -t capella/base capella --build-arg INJECT_PACKAGES=true
```

#### Option 2: Download Capella archive automatically

If you choose to download Capella automatically, then all you have to do is run the following command:

```zsh
docker build -t capella/base capella --build-arg BUILD_TYPE=online --build-arg CAPELLA_VERSION=$CAPELLA_VERSION
```

where `$CAPELLA_VERSION` should be replaced with the Capella version (e.g. `5.2.0`).
If a suitable version is found, it will be downloaded.

### 3. Docker image `t4c/client/base`

The T4C base image builds on top of the Capella base image and installs the T4C client
plugins.

1) Download a Team for Capella client for Linux from
   <https://www.obeosoft.com/en/team-for-capella-download>

   Note that the T4C client version must match the version for Capella itself.
   To obtain a Linux T4C client version below 5.2 you may want to contact
   [Obeo](https://www.obeosoft.com/en/team-for-capella-download) to get a bundle.

1) Extract the downloaded archive. The extracted folder comes with a `.zip` file
   containing the T4C client:

   ```text
   $ tree -L 2 TeamForCapella-5.0.0-linux.gtk.x86_64
   TeamForCapella-5.0.0-linux.gtk.x86_64
   ├── (...)
   └── updateSite
       └── com.thalesgroup.mde.melody.team.license.update-5.0.0-202012091024.zip
   ```

1) That extracted `.zip` file needs to be copied into the subdirectory `t4c/updateSite`
   of the present repository.

1) Build the container:

   ```zsh
   docker build -t t4c/client/base t4c
   ```

### 4. Docker images `capella/remote` and `t4c/client/remote`

The remote images allow to extend the

- Capella base image (`capella/base`) or
- the T4C base image (`t4c/client/base`)

with an RDP server, a metrics endpoint to measure the container activity and a fileservice that serves the current workspace structure.

It is a basic Linux server with an [Openbox](http://openbox.org/) installation.

Feel free to adjust the configurations `remote/rc.xml` and `remote/menu.xml` to satisfy
custom Openbox configuration needs.

If you like to use your own wallpaper, replace `remote/wallpaper.png`.

In general, no additional configuration is necessary for the build of the remote image:

- Remote image using Capella:

  ```zsh
  docker build -t capella/remote remote --build-arg BASE_IMAGE=capella/base
  ```

- Remote image using T4C Client:

  ```zsh
  docker build -t t4c/client/remote remote --build-arg BASE_IMAGE=t4c/client/base
  ```

### 5. Docker images `capella/ease` and `t4c/client/ease`

The EASE images build on top of the Capella base image or the T4C base image
respectively. They extend the base image with support for Python EASE scripts.
These EASE scripts will run automatically.

If your network is unrestricted, you can build an EASE image with the following command,
whereby you replace `$BASE` with `capella` or `t4c/client`.

```zsh
docker build -t $BASE/ease \
    --build-arg BASE_IMAGE=$BASE/base \
    --build-arg BUILD_TYPE=online \
    ease
```

If your network is restricted, please execute the steps described in
[Download Eclipse Packages manually](#download-eclipse-packages-manually). When your extensions are
located in `ease/extensions` and the right subfolders, please run:

```zsh
docker build -t $BASE/ease \
    --build-arg BASE_IMAGE=$BASE/base \
    --build-arg BUILD_TYPE=offline \
    ease
```

Please replace $BASE with `capella` or `t4c/client`.

### 6. Docker images `capella/cli` and `t4c/client/cli`

The CLI images are meant to have a containerised Capella (with and without a
Team for Capella client) that can be run headless (as command line interface).

Both images build on top of the Capella base image or the T4C base image
respectively. They extend the base image with a virtual display and consider
an entrypoint that forwards all incoming command line flags to the capella
executable.

You can build a CLI image with the following command,
whereby you replace `$BASE` with `capella` or `t4c/client`.

```zsh
docker build -t $BASE/cli --build-arg BASE_IMAGE=$BASE/base cli
```

### 7. Docker image `capella/readonly`

The read-only image builds on top of the Capella EASE remote image and provides support for the read-only use of models.
It clones a git repositories and automatically injects the cloned models in the workspace.

To build the image, please run:

```zsh
docker build -t $BASE/capella/readonly \
    --build-arg BASE_IMAGE=$BASE/capella/ease/remote \
    readonly
```

## Run the images

### Capella in a remote container

```zsh
docker run -d \
    -p $RDP_EXTERNAL_PORT:3389 \
    -e RMT_PASSWORD=$RMT_PASSWORD \
    -e AUTOSTART_CAPELLA=$AUTOSTART_CAPELLA \
    -e RESTART_CAPELLA=$RESTART_CAPELLA \
    capella/remote
```

Please replace the followings variables:

- `$RDP_EXTERNAL_PORT` to the external port for RDP on your host (usually `3389`)
- `$RMT_PASSWORD` is the password for remote connections (for the login via RDP) and has
  to be at least 8 characters long.
- `AUTOSTART_CAPELLA` defines the autostart behaviour of Capella. When set to 1 (default), Capella will be started as soon
  as an RDP connection has been established to the running container.
- `RESTART_CAPELLA` defines the restart behaviour of Capella. When set to 1 (default) and when `AUTOSTART_CAPELLA=1`,
  Capella will be re-started as soon as it has been exited (after clean quits as
  well as crashs).

After starting the container, you should be able to connect to
`localhost:$RDP_EXTERNAL_PORT` with your preferred RDP Client.

For the login use the followings credentials:

- **Username**: `techuser`
- **Password**: `$RMT_PASSWORD`

Capella should then start automatically.

### T4C client in a remote container

```zsh
docker run -d \
    -p $RDP_EXTERNAL_PORT:3389 \
    -e T4C_LICENCE_SECRET=XXX \
    -e T4C_SERVER_HOST=$T4C_SERVER_HOST \
    -e T4C_SERVER_PORT=$T4C_SERVER_PORT \
    -e T4C_REPOSITORIES=$T4C_REPOSITORIES \
    -e RMT_PASSWORD=$RMT_PASSWORD \
    -e FILESERVICE_PASSWORD=$FILESERVICE_PASSWORD \
    -e T4C_USERNAME=$T4C_USERNAME \
    -e AUTOSTART_CAPELLA=$AUTOSTART_CAPELLA \
    -e RESTART_CAPELLA=$RESTART_CAPELLA \
    t4c/client/remote
```

Please replace the followings variables:

- `$RDP_EXTERNAL_PORT` to the external port for RDP on your host (usually `3389`)
- `$RMT_PASSWORD` is the password for remote connections (for the login via RDP).
- `$T4C_LICENCE_SECRET` to your TeamForCapella licence secret.
- `$T4C_SERVER_HOST` to the IP-Address of your T4C server (default: `127.0.0.1`).
- `$T4C_SERVER_PORT` to the port of your T4C server (default: `2036`).
- `$T4C_REPOSITORIES` is a comma-seperated list of repositories. These repositories show
  up as default options on connection (e.g. `repo1,repo2`).
- `$T4C_USERNAME` is the username that is suggested when connecting to t4c.
- `$FILESERVICE_PASSWORD` with the password for the fileservice, which is used as basic authentication password.
- `AUTOSTART_CAPELLA` defines the autostart behaviour of Capella. When set to 1 (default), Capella will be started as soon
  as an RDP connection has been established to the running container.
- `RESTART_CAPELLA` defines the restart behaviour of Capella. When set to 1 (default) and when `AUTOSTART_CAPELLA=1`,
  Capella will be re-started as soon as it has been exited (after clean quits as
  well as crashs).

After starting the container, you should be able to connect to
`localhost:$RDP_EXTERNAL_PORT` with your preferred RDP Client.

Please use the followings credentials:

- **Username**: `techuser`
- **Password**: `$RMT_PASSWORD`

Capella should then start automatically. You should be able to connect to T4C models
out of the box.

The screen size is set every time the connection is established. Depending on your
RDP client, you will also be able to set the preferred screen size in the settings.

By default, Remmina (RDP client for Linux) starts in a tiny window. To fix that, you can
easily set "Use client resolution" instead of "Use initial window size" in the remote
connection profile.

We also plan to integrate "dynamic resizing" in the near future.

### EASE container

Run the image with this command and provide EASE Python scripts as a volume.
The scripts have to be located in the `/opt/scripts` directory (inside the container)!

For more information refer to: [How does a EASE Python Script look like?](#how-does-an-ease-python-script-look-like).

To run the container, just execute:

```zsh
docker run -v script.py:/opt/scripts/script.py $BASE/ease
```

where `$BASE` is again `capella` or `t4c/client`.

### CLI container

```zsh
docker run $BASE/cli -nosplash -consolelog -application APPLICATION -appid APPID [...]
```

with `$BASE` being one out of `capella` or `t4c/client`.

**Example to export representations (diagrams) as SVG images:**

Replace `/path/to/model` and `<PROJECT_NAME>` to pass any local Capella
model. Set the project name so that it fits your Capella project name for the
model as it is given in the file `/path/to/model/.project`.

Exported diagrams will appear on the host machine at
`/path/to/model/diagrams`.

```zsh
docker run --rm -it \
  -v /path/to/model:/model \
  capella/cli \
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

### Read-only container

There are two options available for read-only containers.
The first option supports multiple repositories, but you need to JSON-serizalize it.
With the second option, you can provide the details as environment variables directly.

For both option, you have to replace the used variables:

- `$RDP_EXTERNAL_PORT` with the external port for RDP on your host (usually `3389`)
- `$EASE_LOG_LOCATION` (optional) with the absolute path to log file. Defaults to `/proc/1/fd/1` (Docker logs) if not provided.

#### Option 1: Provide repository details as JSON

With this option, any number of models can be loaded.
These must first be serialized to JSON in the following format:

```json
[
  {
    "url": "https://github.com/DSD-DBS/py-capellambse.git", # Path that is used by 'git clone'
    "revision": "master",
    "depth": 1, # Optional: If depth == 0, the whole history is cloned. Defaults to 0
    "entrypoint": "tests/data/melodymodel/5_2/Melody Model Test.aird", # Path to the aird file, starting from the root of the repository
    "nature": "project", # Optional: Can be either 'project' or 'library'. Defaults to 'project'
    "username": "testuser", # Optional: Only need if repository access is restricted
    "password": "token" # Optional: Only need if repository access is restricted
  }
]
```

The JSON string has to be provided as value to the environment variable with the key `GIT_REPOS_JSON`:

```zsh
docker run -d \
    -p $RDP_EXTERNAL_PORT:3389 \
    -e RMT_PASSWORD=$RMT_PASSWORD \
    -e GIT_REPOS_JSON=$GIT_REPOS_JSON \
    -e EASE_LOG_LOCATION=$EASE_LOG_LOCATION \
    capella/readonly
```

Please replace the `GIT_REPOS_JSON` with the JSON-string (described above).

#### Option 2: Provide repository details directly

With this option, you can only provide details for exactly one repository at time.
If you want to make any number of models available, please use option 1.

```zsh
docker run -d \
    -p $RDP_EXTERNAL_PORT:3389 \
    -e RMT_PASSWORD=$RMT_PASSWORD \
    -e GIT_URL=$GIT_URL \
    -e GIT_ENTRYPOINT=$GIT_ENTRYPOINT \
    -e GIT_REVISION=$GIT_REVISION \
    -e GIT_DEPTH=$GIT_DEPTH \
    -e GIT_USERNAME=$GIT_USERNAME \
    -e GIT_PASSWORD=$GIT_PASSWORD \
    -e EASE_LOG_LOCATION=$EASE_LOG_LOCATION \
    capella/readonly
```

Please replace the followings variables (in addition to the general variables):

- `$GIT_URL` with the URL to the Git repository. All URI-formats supported by the `git clone` command will work. Please do NOT include credentials in the URL as they will be not cleaned after cloning the model. You can provide HTTP credentials via the `GIT_USERNAME` and `GIT_PASSWORD` variables (see below).
- `$GIT_ENTRYPOINT` with the relative path from the root of your repository to the `aird`-file of your model, e.g. `path/to/model.aird`.
- `$GIT_REVISION` with the desired revision of the git repository. The revision is cloned with the `--single-branch` option, therefore only the specific revision is accessible. Only tags and branches are supported, commit hashes are NOT supported. If empty, the whole repository gets cloned.
- `$GIT_DEPTH` with the desired git depth. If not provided, the whole history will be cloned.
- `$GIT_USERNAME` with the git username if the repository is access protected. Leave empty, when no authentication is required.
- `$GIT_PASSWORD` with the git password if the repository is access protected. Leave empty, when no authentication is required. The password gets cleaned after cloning and is not accessible in the RDP connection.

## Additional notes

### Tips

- You can mount a Capella workspace inside the container by appending the follwing to
  the `docker run` command:

  ```zsh
  -v /path/to/your/local/volume:/workspace
  ```

### Dockerfile guidelines

We tried to follow the common recommendations for writing Dockerfiles.

We have explicitly observed the following:

- We use the package manager interface `apt-get`, because `apt` does not have a stable
  CLI interface and is not recommended to use it in scripts.

- We tried to reduce the number of layers and to group commands as much as possible.
  However, in some cases we use caching and in other cases it was not always possible
  to group everything for reasons of clarity.

### Download older packages manually

Unfortunately the version `2.28.1` of `libwebkit2gtk-4.0-37` is no longer available in
the default Debian `bullyseye-updates` registry, but it is still available in the
Ubuntu `focal` repository (<https://packages.ubuntu.com/focal/libwebkit2gtk-4.0-37>).

First of all, you have to add the source to your `apt`-sources and add the apt keys.

Recommandation: Spawn a Docker container and execute the steps inside the container.

```zsh
echo "deb http://de.archive.ubuntu.com/ubuntu/ focal main"
apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 3B4FE6ACC0B21F32
apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 871920D1991BC93C
apt update
```

Please download all packages and place the files in the folder `capella/libs`:

- `libicu66_66.1-2ubuntu2_amd64.deb` \
  (Run `apt download libicu66=66.1-2ubuntu2`)

- `libjavascriptcoregtk-4.0-18_2.28.1-1_amd64.deb` \
  (Run `apt download libjavascriptcoregtk-4.0-18=2.28.1-1`)

- `libjpeg-turbo8_2.0.3-0ubuntu1_amd64.deb` \
  (Run `apt download libjpeg-turbo8=2.0.3-0ubuntu1`)

- `libjpeg8_8c-2ubuntu8_amd64.deb` \
  (Run `apt download libjpeg8=8c-2ubuntu8`)

- `libwebkit2gtk-4.0-37_2.28.1-1_amd64.deb` \
  (Run `apt download libwebkit2gtk-4.0-37=2.28.1-1`)

### Download Eclipse packages manually

If your network is restricted and doesn't have access to the public Eclipse registries,
you have to manually download and inject the packages. Luckily capella is an
application build within eclipse which offers a command line tool for downloading
resources from eclipse software repositories. Refer to [this wiki article](https://wiki.eclipse.org/Equinox_p2_Repository_Mirroring#Running_the_Mirroring_Tools) if you
are interested to learn the capabilities of the eclipse mirroring tool.

You have to run the following commands for each of these following urls to download the
metadata and artifact for the packages:

- <https://eclipse.py4j.org/>
- <https://download.eclipse.org/ease/integration/nightly/>
- <https://download.eclipse.org/technology/swtbot/releases/latest/>

```zsh
capellac -nosplash -verbose
-application org.eclipse.equinox.p2.artifact.repository.mirrorApplication
-source <url>
-destination <destionation_path> (e.g. file:ease/extensions/<extension>)>
```

```zsh
capellac -nosplash -verbose
-application org.eclipse.equinox.p2.metadata.repository.mirrorApplication
-source <url>
-destination <destionation_path> (e.g. file:ease/extensions/<extension>)>
```

where `<extension>` is `py4j`, `ease` or `swtbot`. `capellac` is the path to the
capella executable laying in the capella directory (capella.zip/capella/capella).
If you have build an AppImage (linux) or a shortcut for it you can also call this
with the displayed options.

Each directory `ease/extensions/<extension>` should have the following structure:

- `content.jar`
- `artifacts.jar`
- `plugins/`
  - `*.jar` files
- `features/`
  - `*.jar` files

### How does an EASE Python script look like?

In general, you can try to execute the Py4J in the Eclipse environment for development
purposes first. When the script is tested, you can use it in our container.

Please make sure that any EASE Python scripts have the `onStartup` comment in the
header. That can be the first line or the first line after the module docstring.
This is required, otherwise the scripts will not be auto-executed.

```python
# onStartup: 0
```

An example script using our PyEclipseEase library could look like:

```python
# onStartup: 0
import pyease.ease

if __name__ == "__main__":
    logger = ease.logger
    ease.log_to_file(os.environ["EASE_LOG_LOCATION"])

    pyease.ease.open_eclipse_perspective("Capella")
    logger.info("Hello world!")

    pyease.ease.kill_capella_process(30)
```
