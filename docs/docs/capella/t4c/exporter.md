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
