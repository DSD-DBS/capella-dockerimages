<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# pure::variants

<!-- prettier-ignore -->
!!! info
    The Docker image name for this image is `<base>/pure-variants` or `<base>/pure-variants`
    where `<base>` is one of the following options:

    - `capella/remote`
    - `t4c/client/remote`
    - `eclipse/remote`

    for remote images or

    - `capella/base`
    - `t4c/client/base`
    - `eclipse/base`

    for local images without the remote feature.

As part of this Docker image, `pure::variants` is installed into the Eclipse
software of the base image. In addition, it has some basic configuration
support, e.g., for setting the license server automatically during runtime.

If the base image is based on Capella, the `pure::variants` Capella plugin is
installed in addition.

## Build it yourself

### Preparation

#### Download the `pure::variants` archive

1.  Download the pure::variants updateSite from the pure::variants download
    site: <https://www.pure-systems.com/pvde-update/> (access restricted,
    license needed). The version on the
    [public website](https://www.pure-systems.com/pv-update/) is not sufficient
    (it's missing important plugins).

    Please select: "pure::variants Archived Update Site with all Extensions"
    for Linux (Tux).

1.  Place the zip-file into `pure-variants/versions/$PURE_VARIANTS_VERSION`.
    `$PURE_VARIANTS_VERSION` is the sematic version of pure::variants, e.g.
    `6.0.0`.

### Build it manually with Docker

1. Start the Docker build:

   ```zsh
   docker build -t <base>/pure-variants \
   	    --build-arg BASE_IMAGE=<base> \
        --build-arg PURE_VARIANTS_VERSION=$PURE_VARIANTS_VERSION \
       pure-variants
   ```

   where `<base>` is one of the options listed in the infobox above.

## Run the container

To run the `pure-variants` images, please follow the instructions to run the
[Capella base](./base.md) or [T4C client base image](capella/t4c/base.md), but
consider the following differences:

- Add the environment variable `$PURE_VARIANTS_LICENSE_SERVER` to the
  `docker run` command. The value is the same as set in the Eclipse GUI when
  running a normal installation, e.g. `http://localhost:8080`.
- Bind the directory containing the `license.lic` file to
  `/inputs/pure-variants/` inside the container.
  ```zsh
  docker run -d \
      -p $RDP_EXTERNAL_PORT:3389 \
      -e RMT_PASSWORD=$RMT_PASSWORD \
      $BASE_IMAGE/remote/pure-variants
  ```
