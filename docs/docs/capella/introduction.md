<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Capella introduction

## Supported versions

Currently, we support Capella versions `5.0.0`, `5.2.0`, `6.0.0`, `6.1.0` and
`7.0.0`.

## Supported architectures

Currently, we support amd64 for all supported Capella version. In addition, we
added support for arm64 starting with Capella `6.0.0`.

## Supported dropins

We have prebuilt images for Capella versions `6.1.0` and `7.0.0`
with a pre-selected set of dropins. Available options are:

- `without-dropins`: Without dropins
- `selected-dropins`: With
  [CapellaXHTMLDocGen](https://github.com/eclipse/capella-xhtml-docgen),
  [DiagramStyler](https://github.com/eclipse/capella/wiki/PVMT),
  [PVMT](https://github.com/eclipse/capella/wiki/PVMT),
  [Filtering](https://github.com/eclipse/capella-filtering),
  [Requirements](https://github.com/eclipse/capella-requirements-vp) and
  [SubsystemTransition](https://github.com/eclipse/capella-sss-transition)

If you need a custom set of dropins, you have two options:

**Option 1**: Mount a dropins folder with additional dropins into
`/opt/capella/dropins` when starting the container.

**Option 2**: Build the `capella/base` Docker image manually. More information:
[Build it yourself](./base.md#build-it-yourself)

## Tagging schema for prebuilt images

The Capella related images are tagged using the following schema:

`$CAPELLA_VERSION-$DROPINS_TYPE-$CAPELLA_DOCKER_IMAGES_REVISION`, e.g.,
`6.0.0-selected-dropins-v1.10.2` for Capella version `6.0.0` with selected
dropins and Capella Docker images revision `v1.10.2`.

`$CAPELLA_VERSION` is the semantic version of Capella (see supported versions
[above](#supported-versions)). `$DROPINS_TYPE` is the name of the set of
dropins. `$CAPELLA_DOCKER_IMAGES_REVISION` can be a tag or branch of this
repository. In case of branches, all characters matching the regex
`[^a-zA-Z0-9.]` will be replaced with `-`.

We don't tag images with the `latest` tag. You may want to use
`$CAPELLA_VERSION-selected-dropins-main` for the latest version, but we
recommend using tags for the best stability.

## Tips

- You can mount a Capella workspace inside the container by appending the
  following to the `docker run` command:
  <!-- prettier-ignore -->
    ```zsh
    -v /path/to/your/local/volume:/workspace
    ```
