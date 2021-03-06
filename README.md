# Capella, T4C Client and EASE Docker images

## Introduction

Please read the <b>complete</b> README carefully first, as some requirements must be met
for the containers to work as desired.

The repository provides Docker images for the followings tools:

- Capella: <https://www.eclipse.org/capella/>
- TeamForCapella client: <https://www.obeosoft.com/en/team-for-capella><br/>
  Right now, we don't provide a Docker image for the server.
- EASE: <https://www.eclipse.org/ease/><br/>
  SWT-Bot: https://www.eclipse.org/swtbot/

This repository includes Docker files to build the following Docker images:

| Name of the Docker image | Short description |
|------|---|
| `base` |This is the base image that has the most important tools pre-installed.|
| `capella/base`|This is the Capella base image. It is a simple container with Capella and the required dependencies installed. No more.|
| `t4c/client/base`|This extends the Capella base image with the T4C client and the dependencies.|
| - `capella/ease`<br>- `t4c/client/ease`|This extends the Capella or T4C client base image with EASE and SWTBot functionality. You can mount every Python script and execute it in a container environment. |
| - `capella/remote`<br>- `t4c/client/remote`|The remote image will add an RDP server on top of any other image. This will provide the user the possibility to connect and work inside the container.|
| -`capella/readonly`<br>- `t4c/client/remote`|This image has capability to clone a Git repository, will load the project into the workspace and also offers RDP.|

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

<b>Make sure that all commands are executed in the root directory of the repository.</b>

### Quick Start

The Quick Start can only be used if the following conditions are met:

- Only the standard configuration is required.
- All files are already in the right place.

If the conditions are not fulfilled, please continue with the next step.

Otherwise, you can simply run the following command to build all images:

```sh
make all
```

### 1. Docker image `base` <a id="base"></a>

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

<b>Important:</b>
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

The Capella base image installs a selected Capella client version. The Capella client
needs to be downloaded and can optionally be customised prior to building the Docker
image.

Download a Capella Linux binary `zip` or `tar.gz` archive. You can get a release
directly from Eclipse. Visit <https://github.com/eclipse/capella/releases>, select a
version and follow the hyperlink labelled `Product` to find a binary release for Linux.

Place the downloaded archive in the subdirectory `capella/archives` of the present
repository and ensure that the end result is either

* `capella/archives/capella.tar.gz` or
* `capella/archives/capella.zip`.

Check that the archive has a structure similar to the following coming with a top level
directory named `capella` and several sub directories and files in it.

For Capella 5.0.0 the structure is illustrated below:

```zsh
$ tree -L 1 capella
capella
????????? artifacts.xml
????????? capella
????????? capella.ini
????????? configuration
????????? dropins
????????? epl-v10.html
????????? features
????????? jre
????????? notice.html
????????? p2
????????? plugins
????????? readme
```

#### Optional: customisation of the Capella client

To customise the Capella client you can

1. extract the downloaded archive,
1. apply any modifications (e. g. installation of plugins and/ or dropins) to it, and
1. compress the modified folder `capella` to get a `capella.zip` or `capella.tar.gz`

again.

#### Workaround of pinned library versions to remove incompatibilities

<b>Note:</b><br/>
<i>This workaround is normally handled in the [Dockerfile](capella/Dockerfile) and it is
only necessary to download below libraries if there are restrictions on your network
that block an access to these libraries when the Docker image is being built.</i>

In some Capella versions, there are incompatiblities with certain versions of the
following libraries:

- `libjavascriptcoregtk-4.0-18` (version `2.32.4`)
- `libwebkit2gtk-4.0-37` (version `2.32.4`)

The workaround is to use version `2.28.1` for both libraries in the container.

So if your build environment restricts access to the latest versions you need to
manually download the packages with the command `apt download` and inject them into the
container.

For more information refer to [Download older packages manually](#debian_packages).

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
   ????????? (...)
   ????????? updateSite
       ????????? com.thalesgroup.mde.melody.team.license.update-5.0.0-202012091024.zip
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

with an RDP server.

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

The EASE image builds on top of the Capella base image or the T4C base image
respectively. It extends the images with support for Python EASE scripts.
These EASE scripts will run automatically.

If your network is unrestricted, you can build an EASE image with the following command,
whereby you replace `$BASE` with `capella` or `t4c/client`.

```zsh
docker build -t $BASE/ease \
    --build-arg BASE_IMAGE=$BASE/base \
    --build-arg BUILD_TYPE=online \
    ease
```

If you network is restricted, please execute the steps described in
[Download Eclipse Packages manually](#eclipse_packages). When your extensions are
located in `ease/extensions` and the right subfolders, please run:

```zsh
docker build -t $BASE/ease \
    --build-arg BASE_IMAGE=$BASE/base \
    --build-arg BUILD_TYPE=offline \
    ease
```
Please replace $BASE with `capella` or `t4c/client`. 

## Run the images

### Capella in a remote container

```zsh
docker run -d \
    -p $RDP_EXTERNAL_PORT:3389 \
    -e RMT_PASSWORD=$RMT_PASSWORD \
    capella/remote
```

Please replace the followings variables:

- `$RDP_EXTERNAL_PORT` to the external port for RDP on your host (usually `3389`)
- `$RMT_PASSWORD` is the password for remote connections (for the login via RDP) and has
  to be at least 8 characters long.

After starting the container, you should be able to connect to
`localhost:$RDP_EXTERNAL_PORT` with your preferred RDP Client.

For the login use the followings credentials:<br>

- <b>Username</b>: `techuser`
- <b>Password</b>: `$RMT_PASSWORD`

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
    -e T4C_USERNAME=$T4C_USERNAME \
    t4c/client/remote
```

Please replace the followings variables:

- `$RDP_EXTERNAL_PORT` to the external port for RDP on your host (usually `3389`)
- `$RMT_PASSWORD` is the password for remote connections (for the login via RDP).
- `$T4C_LICENCE_SECRET` to your TeamForCapella licence secret.
- `$T4C_SERVER_HOST` to the IP-Address of your T4C server (default: `127.0.0.1`).
- `$T4C_SERVER_PORT` to the port of your T4C server (default: `2036`).
- `$T4C_REPOSITORIES` is a comma-seperated list of repositories. These repositories show
  up as default options on connection (e.g. `repo1,repo2`).- `$T4C_USERNAME` is the username that is suggested when connecting to t4c.

After starting the container, you should be able to connect to
`localhost:$RDP_EXTERNAL_PORT` with your preferred RDP Client.

Please use the followings credentials: <br>

- <b>Username</b>: `techuser`
- <b>Password</b>: `$RMT_PASSWORD`

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

For more information refer to: [How does a EASE Python Script look like?](#python_ease).

To run the container, just execute:

```zsh
docker run -v script.py:/opt/scripts/script.py $BASE/ease
```

where `$BASE` is again `capella` or `t4c/client`.

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

### <a id="debian_packages"></a>Download older packages manually

Unfortunately the version `2.28.1` of `libwebkit2gtk-4.0-37` is no longer available in
the default Debian `bullyseye-updates` registry, but it is still available in the
Ubuntu `focal` repository (https://packages.ubuntu.com/focal/libwebkit2gtk-4.0-37).

First of all, you have to add the source to your `apt`-sources and add the apt keys.

Recommandation: Spawn a Docker container and execute the steps inside the container.

```zsh
echo "deb http://de.archive.ubuntu.com/ubuntu/ focal main"
apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 3B4FE6ACC0B21F32
apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 871920D1991BC93C
apt update
```

Please download all packages and place the files in the folder `capella/libs`:

- `libicu66_66.1-2ubuntu2_amd64.deb`<br>
  (Run `apt download libicu66=66.1-2ubuntu2`)

- `libjavascriptcoregtk-4.0-18_2.28.1-1_amd64.deb`<br>
  (Run `apt download libjavascriptcoregtk-4.0-18=2.28.1-1`)

- `libjpeg-turbo8_2.0.3-0ubuntu1_amd64.deb`<br>
  (Run `apt download libjpeg-turbo8=2.0.3-0ubuntu1`)

- `libjpeg8_8c-2ubuntu8_amd64.deb`<br>
  (Run `apt download libjpeg8=8c-2ubuntu8`)

- `libwebkit2gtk-4.0-37_2.28.1-1_amd64.deb`<br>
  (Run `apt download libwebkit2gtk-4.0-37=2.28.1-1`)

### <a id="eclipse_packages"></a>Download Eclipse packages manually

If your network is restricted and doesn't have access to the public Eclipse registries,
you have to manually download and inject the packages.

You have to run the following commands for each of these following urls to download the
metadata and artifact for the packages:

- https://eclipse.py4j.org/
- https://download.eclipse.org/ease/integration/nightly/
- https://download.eclipse.org/technology/swtbot/releases/latest/

```zsh
capellac -nosplash -verbose
-application org.eclipse.equinox.p2.artifact.repository.mirrorApplication
-source <url>
-destination <destionation_path> (e.g. file:ease/extensions/<extension>)>
```
```
capellac -nosplash -verbose
-application org.eclipse.equinox.p2.metadata.repository.mirrorApplication
-source <url>
-destination <destionation_path> (e.g. file:ease/extensions/<extension>)>
```

where `<extension>` is `py4j`, `ease` or `swtbot`.

Each directory `ease/extensions/<extension>` should have the following structure:

- `content.jar`
- `artifacts.jar`
- `plugins/`
    - `*.jar` files
- `features/`
    - `*.jar` files

### <a id="python_ease"></a>How does an EASE Python script look like?

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
