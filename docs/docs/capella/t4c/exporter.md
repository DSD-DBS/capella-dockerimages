<!--
 ~ SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# T4C client exporter

<!-- prettier-ignore -->
!!! info
    The Docker image name for this image is `t4c/client/exporter`

<!-- prettier-ignore -->
!!! info
    The exporter can export a model from Git to a TeamForCapella repository with the `merge`-strategy of TeamForCapella.

The T4C client exporter image imports a model from a git repository and exports it to a T4C server.

## Build it yourself

### Build it manually with Docker

To build the image, please run:

```zsh
docker build -t t4c/client/exporter \
    --build-arg BASE_IMAGE=t4c/client/base \
    exporter
```

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
  -e HTTP_PORT=8080 \
  -e HTTP_LOGIN=admin \
  -e HTTP_PASSWORD=password \
  -e LOG_LEVEL=DEBUG \
  t4c/client/exporter
```

You can find the description for most of the values in the run instructions of the [importer](./importer.md#run-the-container). These are the additional ones:

- `HTTP_PORT`: port to the T4C http server
- `HTTP_LOGIN`: username for the REST API. At the moment administrator access is required
- `HTTP_PASSWORD`: password for the REST API
