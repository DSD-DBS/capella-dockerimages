<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# TeamForCapella client backup / importer

<!-- prettier-ignore -->
!!! info
    The Docker image name for this image is `t4c/client/base`

<!-- prettier-ignore -->
!!! info
    The importer exports a model from a TeamForCapella repository to a Git repository.

The T4C client backup image imports a model from a TeamForCapella server and
exports it to a Git repository. It can be used as a backup solution, for
example, in a scheduled job.

## Build it yourself

### Build it manually with Docker

Build instructions are the same as the [T4C client base](base.md) image.

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

    For the next steps, you need a running TeamForCapella server.

<!-- prettier-ignore -->
1. Start a lightweight local Git server with the following command:
   ```zsh
   make run-local-git-server
   ```

1. Create a new TeamForCapella repository via the REST API.
   If you want to include the user information in the commits, you have to enable authentication.
1. Set the `T4C_REPO_NAME` environment variable to the repository name that you
   chose in the previous step:

    ```zsh
    export T4C_REPO_NAME="repoCapella"
    ```

1. Open Capella and create a new Capella project with the project name "test".
1. [Export the project to the TeamForCapella repository](https://dsd-dbs.github.io/capella-collab-manager/user/tools/capella/teamforcapella/export/export-to-t4c/)
1. Run the following command to start the importer:

    ```zsh
    make run-t4c/client/backup
    ```

1. Clone the sample repository:

    ```zsh
    git clone 'http://localhost:10001/git/git-test-repo.git'
    ```

1. Check the commit history and the model in the repository.
