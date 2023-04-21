<!--
 ~ SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

## Supported versions

Currently, we support Capella versions `5.0.0`, `5.2.0` and `6.0.0`.

## Supported architectures

Currently, we support amd64 for all supported Capella version.
In addition, we added support for arm64 starting with Capella `6.0.0`.

## Tagging schema for prebuilt images

The Capella related images are tagged using the following schema:

`$CAPELLA_VERSION-$CAPELLA_DOCKER_IMAGES_REVISION`, e.g., `6.0.0-v1.10.2` (for Capella version `6.0.0` and Capella Docker images revision `v1.10.2`).

`$CAPELLA_VERSION` is the semantic version of Capella (see supported versions [above](#supported-versions)).
`$CAPELLA_DOCKER_IMAGES_REVISION` can be a tag or branch of this repository. In case of branches, all characters matching the regex `[^a-zA-Z0-9.]` will be replaced with `-`.

We don't tag images with the `latest` tag. You may want to use `$CAPELLA_VERSION-main` for the latest version, but we recommend using tags for the best stability.

## Tips

- You can mount a Capella workspace inside the container by appending the following to
  the `docker run` command:
  <!-- prettier-ignore -->
    ```zsh
    -v /path/to/your/local/volume:/workspace
    ```
