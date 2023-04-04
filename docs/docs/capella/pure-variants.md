<!--
 ~ SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Capella + pure::variants

<!-- prettier-ignore -->
!!! info
    The Docker image name for this image is `capella/remote/pure-variants` or `t4c/client/remote/pure-variants`

This Docker image adds the `pure::variants` Capella plugin and allows the definition of a pure variants license server during runtime.

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

1. Download the pure::variants updateSite from the pure::variants download site: <https://www.pure-systems.com/pvde-update/> (access restricted, license needed).
   The version on the [public website](https://www.pure-systems.com/pv-update/) is not sufficient (it's missing important plugins).

   Please select: "pure::variants Archived Update Site with all Extensions" for Linux (Tux).

1. Place the zip-file into `pure-variants/updateSite`.

### Build it manually with Docker

1. Start the Docker build:

   ```zsh
   docker build -t t4c/client/remote/pure-variants \
       --build-arg CAPELLA_VERSION=$CAPELLA_VERSION \
       --build-arg
       pure-variants
   ```

## Run the container

To run the `pure-variants` images, please follow the instructions to run the [Capella base](../base.md) or [T4C client base image](../t4c/base.md), but consider the following differences:

- Add the environment variable `$PURE_VARIANTS_LICENSE_SERVER` to the `docker run` command. The value is the same as set in the Capella GUI when running a normal installation, e.g. `http://localhost:8080`.
- Bind the directory containing the `license.lic` file to `/inputs/pure-variants/` inside the container.
  ```zsh
  docker run -d \
      -p $RDP_EXTERNAL_PORT:3389 \
      -e RMT_PASSWORD=$RMT_PASSWORD \
      $BASE_IMAGE/remote
  ```
