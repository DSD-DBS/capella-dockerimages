<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Jupyter Base

The `jupyter` image provides a JupyterLab server with some additional
configuration options.

The image is configured to connect to the same workspace shared volume as the
Capella remote images. If the `notebooks/` folder on the shared volume contains
a `requirements.txt` file, dependencies defined in that file will be installed
before the server launches.

```zsh
docker build -t jupyter jupyter
```

## Run the `jupyter` image

```zsh
docker run -ti --rm -e WORKSPACE_DIR=/tmp/notebooks -p 8888:8888 jupyter-notebook
```

The following environment variables can be defined:

- `JUPYTER_PORT`: The port to run the jupyter server on.
- `WORKSPACE_DIR`: The working directory for JupyterLab.
- `JUPYTER_BASE_URL`: A context path to access the jupyter server. This allows
  you to run multiple server containers on the same domain.
- `JUPYTER_ADDITIONAL_DEPENDENCIES`: A space-separated list of additional pip
  dependencies to install. The variable is passed to the `pip install -U`
  command and may include additional flags. The value is not escaped, only use
  trusted values.
