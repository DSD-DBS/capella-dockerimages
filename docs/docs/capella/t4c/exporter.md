<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# TeamForCapella client exporter

<!-- prettier-ignore -->
!!! info
    The Docker image name for this image is `t4c/client/base`

<!-- prettier-ignore -->
!!! info
    The exporter can export a model from Git to a TeamForCapella repository with the `merge`-strategy of TeamForCapella.

The T4C client exporter image imports a model from a git repository and exports
it to a T4C server.

## Build it yourself

### Build it manually with Docker

Build instructions are the same as the [T4C client base](base.md) image.

## Run the container

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
[importer](./importer.md#run-the-container).

## Testing

### Manual Testing

For development purposes, you can test the exporter locally.

!!! warning

    For the next steps, you need a running TeamForCapella server.

<!-- prettier-ignore -->
1. Start a lightweight local Git server with the following command:
   ```zsh
   make run-local-git-server
   ```
1. Clone the sample repository:
   ```zsh
   git clone 'http://localhost:10001/git/git-test-repo.git'
   ```
1. Copy the model to the newly created repository. Push the model you'd like to
   export:

    ```zsh
    git add .
    git commit -m "Initial commit"
    git push
    ```

1. Set the `GIT_REPO_ENTRYPOINT` environment variable to the relative path from
   the root of the repository to the aird file:

    ```zsh
    export GIT_REPO_ENTRYPOINT="path/to/your/model.aird"
    ```

1. Create a new TeamForCapella repository via the REST API.
1. Set the `T4C_REPO_NAME` environment variable to the repository name that you
   chose in the previous step:

    ```zsh
    export T4C_REPO_NAME="repoCapella"
    ```

1. Run the following command to start the exporter:
    ```zsh
    make run-t4c/client/exporter
    ```
1. Connect to the repository from a Capella client to verify that the model was
   exported correctly.
