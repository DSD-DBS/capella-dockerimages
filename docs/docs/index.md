<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Introduction

Welcome to the MBSE Docker images repository. Initially started for our
[Capella Collaboration Manager](https://github.com/DSD-DBS/capella-collab-manager)
to run Capella in a browser, we now offer a variety of Docker images to
automate processes in the MBSE context, which can be extended with compatible
extensions.

<div class="grid cards" markdown>

<!--prettier-ignore-->
-  ![Capella icon](./base/capella/logo.png){: .middle style="height:30px" } __Capella__

    ---

    Eclipse Capella client.

    [:octicons-arrow-right-24: Build & Customize locally](./base/capella/index.md#build-it-yourself) <br>
    [:octicons-arrow-right-24: Use pre-built images from ghcr.io](./base/capella/index.md#use-the-prebuilt-image)

    Available extensions:

    [:material-tab-plus: Remote extension](./extensions/remote.md) <br>
    [:material-tab-plus: TeamForCapella extension](./extensions/t4c.md) <br>
    [:material-tab-plus: pure::variants extension](./extensions/pure-variants.md)

-   ![Papyrus icon](./base/papyrus/logo.png){: .middle style="height:30px" } __Papyrus__

    ---

    Eclipse Papyrus client.

    [:octicons-arrow-right-24: Build & Customize locally](./base/papyrus/index.md)
    <br> <br>

    Available extensions:

    [:material-tab-plus: Remote extension](./extensions/remote.md)

-   ![Eclipse icon](./base/eclipse/logo.png){: .middle style="height:30px" } __Eclipse__

    ---

    Eclipse IDE with EGit preinstalled.

    [:octicons-arrow-right-24: Build & Customize locally](./base/eclipse/index.md)

    Available extensions:

    [:material-tab-plus: Remote extension](./extensions/remote.md) <br>
    [:material-tab-plus: pure::variants extension](./extensions/pure-variants.md)

-  ![Jupyter icon](./base/jupyter/logo.png){: .middle style="height:30px" } __Jupyter__

    ---

    Jupyter customized with Capella libraries.

    [:octicons-arrow-right-24: Build & Customize locally](./base/jupyter/index.md)

</div>

## Prerequisites for Local Image Building

If you want to build the images locally, clone this repository:

```zsh
git clone https://github.com/DSD-DBS/capella-dockerimages.git
```

We use buildpacks to build the images. To install the pack CLI, follow
[these instructions](https://buildpacks.io/docs/for-platform-operators/how-to/integrate-ci/pack/).

We use experimental features of buildpacks. To enable experimental support,
run:

```zsh
pack config experimental true
```

If you want to learn why we use buildpacks, you can read more about it
[here](./development/buildpacks.md).

## Build Images with GNU Make

If you have [GNU Make](https://www.gnu.org/software/make/manual/make.html)
installed on your system, you can make use of our Makefile to build, run and
debug our Docker images.

!!! warning

    The minimum required GNU Make version is `3.82`, however we recommend version `4.X`. Use version `4.4` for the best experience. The **preinstalled Make version on macOS is `3.81` and is not supported by us**. Please update the version to >= `3.82`.

!!! info

    When running the build targets with `PUSH_IMAGES=1`, they get pushed to your preferred registry after each build.

For each image, please execute the steps described in the preparation section
in the corresponding documentation.

## Build images in a CI/CD environment

We provide a
[Gitlab CI/CD template](https://github.com/DSD-DBS/capella-dockerimages/blob/main/ci-templates/gitlab/image-builder.yml)
to build and test the images in CI/CD environment. Please find the instructions
[here](https://github.com/DSD-DBS/capella-dockerimages/tree/main/ci-templates/gitlab#image-builder).
