# Capella, T4C Client and EASE Dockerimages

## Introduction
Please read the <b>complete</b> README file carefully first, as some requirements must be met for the containers to work as desired. <br>
The repository provides Dockerimages for the followings Tools: 
- Capella: https://www.eclipse.org/capella/
- T4C Client: https://www.obeosoft.com/en/team-for-capella <br>
Right now, we don't provide a Dockerimage for the Server. 
- EASE: https://www.eclipse.org/ease/<br>
SWT-Bot: https://www.eclipse.org/swtbot/

This repository includes Dockerfiles to build the following Dockerimages:

| Name of the Dockerimage | Short Description |
|------|---|
| base |This is the base image that has the most important tools pre-installed.|
|capella/base|This is the Capella Baseimage. It is a simple Container with Capella and the required dependencies installed. No more.|
|t4c/client/base|This extends the Capella Baseimage with the T4C Client and the dependencies.|
|capella/ease<br>t4c/client/ease|This extends the Capella or T4C Client Baseimage with EASE and SWTBot Functionality. You can mount every Python-Script and execute it in a Container environment. |
|capella/remote <br> t4c/client/remote|The Remoteimage will add a RDP server on top of any other image. This will provide the user the possibility to connect and work inside the Container.|

Important for building the images is to strictly follow the sequence: 
- <b>capella/base</b> depends on <b>base</b>
- <b>t4c/client/base</b> depends on <b>capella/base</b>
- <b>capella/ease</b> depends on <b>capella/base</b>
- <b>t4c/client/ease</b> depends on <b>t4c/client/base</b>
- <b>capella/remote</b> depends on <b>capella/base</b>
- <b>t4c/client/remote</b> depends on <b>t4c/client/base</b>

## Build the Images

<b>Make sure that all commands are executed in the root directory of the repository.</b>

### 1. Base
Our Baseimage updates the packages and installs the following packages: 
- `python3-pip`
- `python3` 

Also, we create a custom user `techuser`. The user will be always used to run the containers and allows to assign a custom UID. This can make sense, if you want to deploy the Containers in a K8s Cluster and your company has some security restrictions (e.g. specific UID ranges). 

Feel free to modify this Image to your specific needs. You are able to set Proxies, custom Registry URLs, your timezone, CA Certificates and any other stuff.

To build the Baseimage, please run: 
```
docker build -t base -f base/Dockerfile
```

<b>Important:</b>
 If you company has a specific Baseimage with all company configurations, of course, it can also be used: 
```
docker build -t base --build-arg=$CUSTOM_IMAGE -f base/Dockerfile
```
Make sure that your `$CUSTOM_IMAGE` is a Linux Image that has the common tools installed and uses the `apt` / `apt-get` Package Manager. If this is not the case, the image cannot be used. Our images were tested with the image `buildpack-deps:bullseye`. 

### 2. Capella Baseimage
The Capella Baseimage installs the Capella Client and Dropins. 
Please follow these steps: 
1) Download the Capella Linux Version as `zip` or `tar.gz` archive. You can get the releases here directly from Eclipse: https://github.com/eclipse/capella/releases
2) Replace the empty file `capella/capella.zip` with your custom Capella `zip` or `tar.gz`. The `capella.zip` oder `capella/capella.tar.gz` should have the following structure (looking at the root of `capella.zip` / `capella.tar.gz`). It is the default structure of the offical releases: 
    - capella
      - configuration
      - features
      - jre
      - p2
      - plugins
      - capella
      - capella.ini
      - (depending on your version, there can be more files)
    - samples
3) Download your dropins (if any)
4) Place your dropins in the folder `capella/dropins`
5) <b>Important:</b> This step is only necessary if there are restrictions on your network. <br>

    In some Capella versions, there are incompatiblities with a certain version of the following libraries: 
        - `libjavascriptcoregtk-4.0-18` in the version `2.32.4`
        - `libwebkit2gtk-4.0-37` in the version `2.32.4`

    For this reason, we use the version `2.28.1` of the two libraries in our container. There are some companies that restrict access to the latest versions only. In such a case you have to download the followings packages with the command `apt download` manually (outside the company network) and inject them manually into the container. Please refer to [Download older packages manually](#debian_packages). 
6) Build the Dockerimage. If you have applied Step 5, please use the following command: 
   ```

   ```

TODO

### 3. T4C Baseimage
TODO

### 4. Remote Images
TODO

### 5. EASE Images
TODO

## Run the Images

### Capella in a Remotecontainer
```
docker run -d \
    -p $RDP_EXTERNAL_PORT:3389 \
    -e BASE_IMAGE=capella \
    -e TYPE=capella \
    -e RMT_PASSWORD=$RMT_PASSWORD \
    capella/remote:$VERSION
```

Please replace the followings variables: 
- `$RDP_EXTERNAL_PORT` to the external Port for RDP on your host (usually `3389`)
- `$RMT_PASSWORD` is the password for remote connections (for the login via RDP).

After starting the Container, you should be able to connect to `localhost:$RDP_EXTERNAL_PORT` with your preferred RDP Client. 
Please use the followings credentials: <br>
<b>Username</b>: `techuser` <br>
<b>Password</b>: `$RMT_PASSWORD`

Capella should then start automatically. 

### T4C Client in a Remotecontainer
```
docker run -d \
    -p $RDP_EXTERNAL_PORT:3389 \
    -e BASE_IMAGE=t4c/client \
    -e TYPE=t4c \
    -e RMT_PASSWORD=$RMT_PASSWORD \
    -e T4C_REPOSITORIES=$T4C_REPOSITORIES \
    t4c/client/remote:$VERSION
```

Please replace the followings variables: 
- `$TYPE` to `capella` or `t4c/client`. If you only need Capella, use `capella`. If you also need the T4C Extension, please use `t4c/client`.
- `$RDP_EXTERNAL_PORT` to the external Port for RDP on your host (usually `3389`)
- `$RMT_PASSWORD` is the password for remote connections (for the login via RDP).
- 
TODO

### EASE Container
TODO

## Additional Notes 

### Dockerfile Guidelines
We tried to follow the common recommendations about writing Dockerfiles. 
We have explicitly observed the following:
- We use the package manager interface `apt-get`, because `apt` does not have a stable CLI interface and is not recommended to use in scripts.
- We tried to reduce the number of layers and to group commands as much as possible. However, in some cases we use caching and in other cases it was not always possible to group everything for reasons of clarity.

### <a id="debian_packages"></a>Download older packages manually

Unfortunately the version `2.28.1` of `libwebkit2gtk-4.0-37` is no longer available in the default Debian `bullyseye-updates` registry, but it is still available in the Ubuntu `focal` repository (https://packages.ubuntu.com/focal/libwebkit2gtk-4.0-37).  and place the files into the folder `capella/libs`:
    - `libicu66_66.1-2ubuntu2_amd64.deb` <br>
    (Run `apt download libicu66=66.1-2ubuntu2`)
    - `libjavascriptcoregtk-4.0-18_2.28.1-1_amd64.deb` <br>
    (Run `apt download libjavascriptcoregtk-4.0-18=2.28.1-1`)
    - `libjpeg-turbo8_2.0.3-0ubuntu1_amd64.deb` <br>
    (Run `apt download libjpeg-turbo8=2.0.3-0ubuntu1`)
    - `libjpeg8_8c-2ubuntu8_amd64.deb` <br>
    (Run `apt download libjpeg8=8c-2ubuntu8`)
    - `libwebkit2gtk-4.0-37_2.28.1-1_amd64.deb` <br>
    (Run `apt download libwebkit2gtk-4.0-37=2.28.1-1`)