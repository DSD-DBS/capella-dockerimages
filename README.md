<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

<!--
SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
SPDX-License-Identifier: Apache-2.0
-->

# MBSE Docker images

[![REUSE status](https://api.reuse.software/badge/github.com/DSD-DBS/capella-dockerimages)](https://api.reuse.software/info/github.com/DSD-DBS/capella-dockerimages)

## Documentation

The documentation has been moved to
[Github Pages](https://dsd-dbs.github.io/capella-dockerimages/).

## Introduction

This repository provides Docker images for the followings tools:

- [Capella](https://www.eclipse.org/capella/)
  - [TeamForCapella client](https://www.obeosoft.com/en/team-for-capella) \
    Right now, we don't provide a Docker image for the server.
  - [EASE](https://www.eclipse.org/ease/) \
    [SWT-Bot](https://www.eclipse.org/swtbot/)
- [Jupyter Notebook](https://jupyter.org/)

In general, we are providing images to run applications in a containerized
environment and to automate processes around the tools.

This repository includes Docker files to build the following Docker images:

| Name of the Docker image                                            | Short description                                                                                                                                                  |
| ------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `base`                                                              | This is the base image that has the most important tools pre-installed.                                                                                            |
| `capella/base`                                                      | This is the Capella base image. It is a simple container with Capella and the required dependencies installed. No more.                                            |
| `t4c/client/base`                                                   | This extends the Capella base image with the T4C client and the dependencies, as well as features to synchronize T4C and Git repositories.                         |
| `capella/ease`<br>`t4c/client/ease`                                 | This extends the Capella or T4C client base image with EASE and SWTBot functionality. You can mount every Python script and execute it in a container environment. |
| `capella/remote`<br>`t4c/client/remote`                             | The remote image will add an RDP server on top of any other image. This will provide the user the possibility to connect and work inside the container.            |
| `capella/readonly`                                                  | This image has capability to clone a Git repository, will load the project into the workspace and also offers RDP.                                                 |
| `capella/remote/pure-variants`<br>`t4c/client/remote/pure-variants` | This extends the remote image with pure::variants support.                                                                                                         |
| `jupyter-notebook`                                                  | A Jupyter notebook image based on the base image.                                                                                                                  |
