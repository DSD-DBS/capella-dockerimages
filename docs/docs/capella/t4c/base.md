<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# TeamForCapella client base

<!-- prettier-ignore -->
!!! info
    The Docker image name for this image is `t4c/client/base`

The T4C base image builds on top of the Capella base image and installs the T4C client
plugins.

## Build it yourself

### Preparation

#### Download TeamForCapella bundle

<!-- prettier-ignore -->
1. Download a Team for Capella client for Linux from
   <https://www.obeosoft.com/en/team-for-capella-download>

    Note that the T4C client version must match the version for Capella itself.
   To obtain a Linux T4C client version below 5.2 you may want to contact
   [Obeo](https://www.obeosoft.com/en/team-for-capella-download) to get a bundle.

1. Extract the downloaded archive. The extracted folder comes with a `.zip` file
   containing the T4C client:

    ```text
    $ tree -L 2 TeamForCapella-5.0.0-linux.gtk.x86_64
    TeamForCapella-5.0.0-linux.gtk.x86_64
    ├── (...)
    └── updateSite
        └── com.thalesgroup.mde.melody.team.license.update-5.0.0-202012091024.zip
    ```

1. That `.zip` file needs to be copied into the subdirectory `t4c/updateSite/$CAPELLA_VERSION`
   of the present repository.

#### Optional: Add feature patches

It is possible to provide feature patches for our t4c base image that are installed
after the initial installation. To install such feature patches, you have to do the
following things.

1. The feature patch `.zip` file needs to be copied into the subdirectory `t4c/updateSite/$CAPELLA_VERSION`
   of the present repository
1. You have to create the `patch_info.csv` file inside the same subdirectory if not yet existing
1. You have to add a new line to the `patch_info.csv` having the following format:

   ```csv
   <feature patch zip file>,<install iu>,<tag>
   ```

   In case that you have one feature patch zip containing different things you want to
   install you can provide multiple _install iu_, each with a whitespace seperated.
   So in this case the `patch_info.csv` would contain a line with the following format:

   ```csv
   <feature patch zip file>,<install iu 1> <install iu 2> ... <install iu n>,<tag>
   ```

Please ensure that the `patch_info.csv` contains an empty line at the end otherwise
the last feature patch might not be installed.

### Build it manually with Docker

Build the container:

```zsh
docker build -t t4c/client/base --build-arg CAPELLA_VERSION=$CAPELLA_VERSION t4c
```

## Run the container

Running the T4C client container is analogous to the Capella Base container. Please run the [instructions of the Capella Base container](../base.md#run-the-container), but add the following environment variables during the `docker run` command:

```zsh
    -e T4C_LICENCE_SECRET=XXX \
    -e T4C_JSON='[{"repository": "", "port": 0, "host": "", "instance": "", "protocol": "ssl"}]' \
    -e T4C_SERVER_HOST=$T4C_SERVER_HOST \
    -e T4C_SERVER_PORT=$T4C_SERVER_PORT \
    -e T4C_REPOSITORIES=$T4C_REPOSITORIES \
    -e T4C_USERNAME=$T4C_USERNAME \
```

Please replace the followings variables:

- `$T4C_LICENCE_SECRET` with your TeamForCapella licence secret.
- `$T4C_USERNAME` with the username that is suggested when connecting to t4c.
- One of the two options:

      - `$T4C_JSON` with a list of repositories with name, host, port and instance name as JSON:
         ```json
         [
            {
               "repository": "repoCapella",
               "host": "localhost",
               "port": 2036,
               "instance": "", //optional, required if the repository names are not unique
               "protocol": "ssl" //optional, defaults to ssl
            }
         ]
         ```

         The environment variables `$T4C_SERVER_HOST`, `$T4C_SERVER_PORT` and `$T4C_REPOSITORIES` will be ignored.

      - Three environment variables:
         - `$T4C_SERVER_HOST` with the IP-Address of your T4C server (default: `127.0.0.1`).
         - `$T4C_SERVER_PORT` with the port of your T4C server (default: `2036`).
         - `$T4C_REPOSITORIES` with a comma-seperated list of repositories. These repositories show
            up as default options on connection (e.g. `repo1,repo2`).

When Capella has started, you should see the T4C models in the dropdown menu of the connection dialog.
