<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# TeamForCapella client base

!!! info ""

    This extension in only available when using `capella` as base.

!!! commercial "Commercial Product"

    TeamForCapella is a commercial product of OBEO. <br>
    More information: <https://www.obeosoft.com/en/team-for-capella>

The T4C base image builds on top of the Capella base image and installs the T4C
client plugins.

## Build it yourself

### Preparation

#### Download TeamForCapella bundle

1.  Download a Team for Capella client for Linux from
    <https://www.obeosoft.com/en/team-for-capella-download>

    Note that the T4C client version must match the version for Capella itself.
    To obtain a Linux T4C client version below 5.2 you may want to contact
    [Obeo](https://www.obeosoft.com/en/team-for-capella-download) to get a
    bundle.

1.  Extract the downloaded archive. The extracted folder comes with a `.zip`
    file containing the T4C client:

    ```text
    $ tree -L 2 TeamForCapella-5.0.0-linux.gtk.x86_64
    TeamForCapella-5.0.0-linux.gtk.x86_64
    ├── (...)
    └── updateSite
       └── com.thalesgroup.mde.melody.team.license.update-5.0.0-202012091024.zip
    ```

1.  That `.zip` file needs to be copied into the subdirectory
    `t4c/updateSite/$CAPELLA_VERSION` of the present repository.

#### Optional: Add feature patches

It is possible to provide feature patches for our t4c base image that are
installed after the initial installation. To install such feature patches, you
have to do the following things.

1.  The feature patch `.zip` file needs to be copied into the subdirectory
    `t4c/updateSite/$CAPELLA_VERSION` of the present repository
1.  You have to create the `patch_info.csv` file inside the same subdirectory
    if not yet existing
1.  You have to add a new line to the `patch_info.csv` having the following
    format:

    ```csv
    <feature patch zip file>,<install iu>,<tag>
    ```

    In case that you have one feature patch zip containing different things you
    want to install you can provide multiple _install iu_, each with a
    whitespace seperated. So in this case the `patch_info.csv` would contain a
    line with the following format:

    ```csv
    <feature patch zip file>,<install iu 1> <install iu 2> ... <install iu n>,<tag>
    ```

Please ensure that the `patch_info.csv` contains an empty line at the end
otherwise the last feature patch might not be installed.

### Build it manually with Docker

Build the container:

```zsh
docker build -t t4c/client/base --build-arg CAPELLA_VERSION=$CAPELLA_VERSION t4c
```

## Run the container

### Capella with T4C client

Running the T4C client container is analogous to the Capella Base container.
Please run the
[instructions of the Capella Base container](../base.md#run-the-container), but
add the following environment variables during the `docker run` command:

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

When Capella has started, you should see the T4C models in the dropdown menu of
the connection dialog.

### TeamForCapella Exporter

!!! info

    The exporter can export a model from Git to a TeamForCapella repository with the `merge`-strategy of TeamForCapella.

The T4C client exporter image imports a model from a git repository and exports
it to a T4C server.

Run the following command to export from Git to T4C:

```zsh
docker run -d \
  -e GIT_REPO_URL=https://github.com/example/example.git \
  -e GIT_REPO_BRANCH=main \
  -e GIT_USERNAME=user \
  -e GIT_PASSWORD=password \
  -e T4C_REPO_HOST=localhost \
  -e T4C_REPO_PORT=2036 \
  -e T4C_REPO_NAME=repoCapella \
  -e T4C_PROJECT_NAME=test \
  -e T4C_USERNAME=user \
  -e T4C_PASSWORD=password \
  -e LOG_LEVEL=DEBUG \
  t4c/client/base export
```

You can find the description for these values in the run instructions of the
[importer](#teamforcapella-importer).

### TeamForCapella Importer

!!! info

    The importer exports a model from a TeamForCapella repository to a Git repository.

The T4C client backup image imports a model from a TeamForCapella server and
exports it to a Git repository. It can be used as a backup solution, for
example, in a scheduled job.

## Run the container

Please run the following command to run the backup from T4C to Git:

```zsh
docker run -d \
  -e GIT_REPO_URL=https://github.com/example/example.git \
  -e GIT_REPO_BRANCH=main \
  -e GIT_USERNAME=user \
  -e GIT_PASSWORD=password \
  -e T4C_REPO_HOST=localhost \
  -e T4C_REPO_PORT=2036 \
  -e T4C_CDO_PORT=12036 \
  -e T4C_REPO_NAME=repoCapella \
  -e T4C_PROJECT_NAME=test \
  -e T4C_USERNAME=user \
  -e T4C_PASSWORD=password \
  -e LOG_LEVEL="DEBUG" \
  -e INCLUDE_COMMIT_HISTORY=false \
  t4c/client/base backup
```

Set the following values for the corresponding keys:

- `GIT_REPO_URL`: URL to the target Git repository where the model will be
  pushed to. All URI-formats supported by the `git clone` command will work.
  You can provide HTTP credentials via the `GIT_USERNAME` and `GIT_PASSWORD`
  variables (see below).
- `GIT_REPO_BRANCH`: branch of the Git repository.
- `GIT_USERNAME`: Git username if the repository is access protected.
- `GIT_PASSWORD`: Git password that is used during cloning from and pushing to
  the Git repository.
- `T4C_REPO_HOST`: hostname to the T4C server. The same value that you enter in
  Capella to connect to a remote repository.
- `T4C_REPO_PORT`: port to the T4C server. The same value that you enter in
  Capella to connect to a remote repository. Defaults to 2036.
- `T4C_REPO_NAME`: T4C repository name. The same value that you enter in
  Capella to connect to a remote repository.
- `T4C_PROJECT_NAME`: name of the Capella project. It's displayed in the
  Capella project explorer and in the last step when connecting to a remote
  repository.
- `T4C_USERNAME`: T4C username that is used during the import. The user needs
  to have access to the repository.
- `T4C_PASSWORD`: T4C password that is used during the import.
- `LOG_LEVEL`: your preferred logging level (all Python logging levels are
  supported).
- `INCLUDE_COMMIT_HISTORY`: `true` or `false` to define if the T4C commit
  history should be exported. Important: Exporting the commit history can take
  a few hours for large models.

## Extract TeamForCapella commit messages to Git

The importer extracts the commit messages from TeamForCapella and adds them to
the Backup commit description. The commit has the format:

```yaml
Backup

- user: admin
  time: '2024-03-25T16:51:27.697000+00:00'
  description: ''
- user: admin
  time: '2024-03-25T16:51:20.523000+00:00'
  description: null
- user: admin
  time: '2024-03-25T16:51:09.755000+00:00'
  description: Second Example commit
- user: admin
  time: '2024-03-25T16:50:57.138000+00:00'
  description: First example commit
```

The commit body is always in the YAML format.

## Testing

### Manual Testing

For development purposes, you can test the importer / backup locally.

!!! warning

    For the next steps, you need a running TeamForCapella server and a TeamForCapella license server.

1.  Start a lightweight local Git server with the following command:

    ```zsh
    make run-local-git-server
    ```

1.  Create a new TeamForCapella repository via the REST API. If you want to
    include the user information in the commits, you have to enable
    authentication.
1.  Set the `T4C_REPO_NAME` environment variable to the repository name that
    you chose in the previous step:

    ```zsh
    export T4C_REPO_NAME="repoCapella"
    ```

1.  Open Capella and create a new Capella project with the project name "test".
1.  [Export the project to the TeamForCapella repository](https://dsd-dbs.github.io/capella-collab-manager/user/tools/capella/teamforcapella/export/export-to-t4c/)
1.  Run the following command to start the importer:

    ```zsh
    make run-t4c/client/backup
    ```

1.  Clone the sample repository:

    ```zsh
    git clone 'http://localhost:10001/git/git-test-repo.git'
    ```

1.  Check the commit history and the model in the repository.

## Testing

### TeamForCapella Exporter

For development purposes, you can test the exporter locally.

!!! warning

    For the next steps, you need a running TeamForCapella server.

1.  Start a lightweight local Git server with the following command:

    ```zsh
    make run-local-git-server
    ```

1.  Clone the sample repository:#

    ```zsh
    git clone 'http://localhost:10001/git/git-test-repo.git'
    ```

1.  Copy the model to the newly created repository. Push the model you'd like
    to export:

    ```zsh
    git add .
    git commit -m "Initial commit"
    git push
    ```

1.  Set the `GIT_REPO_ENTRYPOINT` environment variable to the relative path
    from the root of the repository to the aird file:

    ```zsh
    export GIT_REPO_ENTRYPOINT="path/to/your/model.aird"
    ```

1.  Create a new TeamForCapella repository via the REST API.
1.  Set the `T4C_REPO_NAME` environment variable to the repository name that
    you chose in the previous step:

    ```zsh
    export T4C_REPO_NAME="repoCapella"
    ```

1.  Run the following command to start the exporter:

    ```zsh
    make run-t4c/client/exporter
    ```

1.  Connect to the repository from a Capella client to verify that the model
    was exported correctly.
