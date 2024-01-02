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

As part of this Docker image, `pure::variants` is installed into the Eclipse software of the base image.
In addition, it has some basic configuration support, e. g., for setting the license server automatically during runtime.

If the base image is based on Capella, the `pure::variants` Capella plugin is installed in addition.

## Build it yourself

### Preparation

#### Optional: Download pure::variants dependencies

_This step in only needed if you don't have internet access in your build environment._

This step is only needed if there is a restricted internet connection in your build environment.

pure::variants needs a subset of the Eclipse 2020-06 repository.
You can find the directory structure here at the bottom of the page: <https://download.eclipse.org/releases/2020-06/202006171000/>

Please download all required files. Your tree should look like:

```text
$ tree pure-variants/dependencies
pure-variants/dependencies
├── artifacts.jar
├── content.jar
└── plugins
    ├── com.google.javascript_0.0.20160315.v20161124-1903.jar
    ├── com.google.protobuf_2.4.0.v201105131100.jar
    ├── org.eclipse.wst.common.core_1.3.0.v201903222010.jar
    ├── org.eclipse.wst.common.environment_1.0.400.v201903222010.jar
    ├── org.eclipse.wst.common.frameworks_1.2.201.v201903222010.jar
    ├── org.eclipse.wst.common.project.facet.core_1.4.400.v201903222010.jar
    ├── org.eclipse.wst.jsdt.core_2.0.303.v202005041016.jar
    ├── org.eclipse.wst.jsdt.manipulation_1.0.601.v201903222047.jar
    ├── org.eclipse.wst.jsdt.ui_2.1.0.v202005221335.jar
    └── org.eclipse.wst.validation_1.2.800.v201904082137.jar
```

#### Download the `pure::variants` archive

1.  Download the pure::variants updateSite from the pure::variants download site: <https://www.pure-systems.com/pvde-update/> (access restricted, license needed).
    The version on the [public website](https://www.pure-systems.com/pv-update/) is not sufficient (it's missing important plugins).

    Please select: "pure::variants Archived Update Site with all Extensions" for Linux (Tux).

1.  Place the zip-file into `pure-variants/versions/$PURE_VARIANTS_VERSION`.
    `$PURE_VARIANTS_VERSION` is the sematic version of pure::variants, e.g. `6.0.0`.

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

To run the `pure-variants` images, please follow the instructions to run the [Capella base](./base.md) or [T4C client base image](capella/t4c/base.md), but consider the following differences:

- Add the environment variable `$PURE_VARIANTS_LICENSE_SERVER` to the `docker run` command. The value is the same as set in the Eclipse GUI when running a normal installation, e.g. `http://localhost:8080`.
- Bind the directory containing the `license.lic` file to `/inputs/pure-variants/` inside the container.
  ```zsh
  docker run -d \
      -p $RDP_EXTERNAL_PORT:3389 \
      -e RMT_PASSWORD=$RMT_PASSWORD \
      $BASE_IMAGE/remote/pure-variants
  ```
