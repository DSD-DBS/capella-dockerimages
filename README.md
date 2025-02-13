<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->


# MBSE Docker images

[![REUSE status](https://api.reuse.software/badge/github.com/DSD-DBS/capella-dockerimages)](https://api.reuse.software/info/github.com/DSD-DBS/capella-dockerimages)

## Introduction

This repository provides containerized clients for the followings tools:

- [Capella](https://www.eclipse.org/capella/)
- [TeamForCapella](https://www.obeosoft.com/en/team-for-capella)
- [Eclipse Papyrus](https://eclipse.dev/papyrus/)
- [Eclipse IDE](https://eclipseide.org/)
- [pure::variants](https://www.pure-systems.com/de/purevariants)
- [Jupyter Notebook](https://jupyter.org/)

The main purposes for containerizing these tools are:

- **Easy to use**: No need to install the tools on your local machine.
- **Reproducibility**: The same environment can be easily reproduced on
  different machines.
- **Isolation**: The tools are isolated from the host machine.
- **Documentation**: All configuration options are documented in the
  Dockerfiles.
- **Collaboration**: The containers can be used in the
  [Collaboration Manager](https://github.com/DSD-DBS/capella-collab-manager)

More information can be found in our
[documentation](https://dsd-dbs.github.io/capella-dockerimages/).
