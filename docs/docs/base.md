<!--
 ~ SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Base image

<!-- prettier-ignore -->
!!! info
    The Docker image name for this image is `base`

Our base image updates all `apt-get` packages and installs the following packages:

- `python3`
- `python3-pip`

Also, we create a custom user `techuser`. This user will always be used to run the
containers and allows to assign a custom `UID`. This can make sense, if you want to
deploy the containers in a K8s cluster and your company has some security restrictions
(e.g. specific `UID` ranges).

Feel free to modify this image to your specific needs. You are able to set proxies,
custom registry URLs, your timezone, CA certificates and any other stuff.

## Use the prebuilt image

```
docker run -it ghcr.io/dsd-dbs/capella-dockerimages/base:$CAPELLA_DOCKER_IMAGES_REVISION
```

where `$CAPELLA_DOCKER_IMAGES_REVISION` is the tag or branch of this repository. In case of branches, replace all characters matching the regex `[^a-zA-Z0-9.]` with `-`.

## Build it yourself

### Build it manually with Docker

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
can not be used. Our images were tested with the image `debian:bookworm`.

If you like to set a custom `UID` for the user `techuser`, you can run:

```zsh
docker build -t base --build-arg UID=1001 base
```
