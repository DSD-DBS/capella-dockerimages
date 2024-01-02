<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

## Build the `jupyter-notebook` image

The `jupyter-notebook` image provides a JupyterLab server that can run on the
Collab-Manager environment.

The image is configured to connect to the same workspace shared volume as the Capella remote images.
If the `notebooks/` folder on the shared volume contains a `requirements.txt` file, dependencies
defined in that file will be installed before the server launches.

```zsh
docker build -t jupyter-notebook jupyter-notebook
```

## Run the `jupyter-notebook` image

```zsh
docker run -ti --rm -e WORKSPACE_DIR=/tmp/notebooks -p 8888:8888 jupyter-notebook
```

The following environment variables can be defined:

- `JUPYTER_PORT`: The port to run the jupyter server on.
- `WORKSPACE_DIR`: The working directory for JupyterLab.
- `JUPYTER_BASE_URL`: A context path to access the jupyter server.
  This allows you to run multiple server containers on the same domain.
- `JUPYTER_TOKEN`: A token for accessing the environment.
