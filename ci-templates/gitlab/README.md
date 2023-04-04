<!--
 ~ SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Gitlab CI templates

Currently, we provide the following Gitlab CI/CD templates:

- [Export to T4C](#export-to-t4c): Export model in repository to T4C using the merge strategy
- [Diagram cache](#diagram-cache): Export diagrams of a Capella model and store them in Gitlab artifacts
- [Image builder](#image-builder): Build and push all Docker images to any Docker registry.
- [Model validation](#model-validation): Runs the Capella model validation CLI tool.

## Export to T4C

Please add the following section to your `.gitlab-ci.yml`:

```yml
variables:
  CAPELLA_VERSION: 6.0.0 # Enter the Capella version of the model here, only versions >= 6.0.0 are supported

include:
  - remote: https://raw.githubusercontent.com/DSD-DBS/capella-dockerimages/${CAPELLA_DOCKER_IMAGES_REVISION}/ci-templates/gitlab/exporter.yml

export-to-t4c:
  variables:
    T4C_REPO_HOST: localhost # Hostname of the T4C server
    T4C_PROJECT_NAME: example # Project name in the T4C repository
    T4C_REPO_NAME: testrepo # T4C repository name
```

In addition, you have to add the following environment variables on repository level.
Make sure to enable the "Expand variable reference" flag.

- `CAPELLA_DOCKER_IMAGES_REVISION`: Revision of this Github repository
- `HTTP_LOGIN` and `HTTP_PASSWORD`: Username / password for the T4C REST API
- `T4C_USERNAME` and `T4C_PASSWORD`: Username / password for the T4C repository

This is the minimal configuration. For more advanced configuration options,
please refer to the [Gitlab CI template](./exporter.yml).

## Diagram cache

Please add the following section to your `.gitlab-ci.yml`:

```yml
variables:
  CAPELLA_VERSION: 6.0.0 # Enter the Capella version of the model here

include:
  - remote: https://raw.githubusercontent.com/DSD-DBS/capella-dockerimages/${CAPELLA_DOCKER_IMAGES_REVISION}/ci-templates/gitlab/diagram-cache.yml

update_capella_diagram_cache:
  variables:
    ENTRY_POINT: test/test.aird # Entry point to the .aird file of the model (relative from root level of the repository)
```

In addition, you have to add the following environment variables on repository level.
Make sure to enable the "Expand variable reference" flag.

- `CAPELLA_DOCKER_IMAGES_REVISION`: Revision of this Github repository

This is the minimal configuration. For more advanced configuration options,
please refer to the [Gitlab CI template](./diagram-cache.yml).

## Image builder

The image builder template builds all images supported by this repository and pushes them to any Docker registry.
We use it in our automated deployment environment for our [Collaboration project](https://github.com/DSD-DBS/capella-collab-manager).
We have restricted internet access in our build environment, so the Gitlab CI is optimized for restricted network access.

Please add the following section to your `.gitlab-ci.yml`:

```yml
include:
  - remote: https://raw.githubusercontent.com/DSD-DBS/capella-dockerimages/${CAPELLA_DOCKER_IMAGES_REVISION}/ci-templates/gitlab/image-builder.yml
```

The resulting images will be tagged in the following format:
`$CAPELLA_VERSION-$CAPELLA_DOCKER_IMAGES_REVISION-$GITLAB_IMAGE_BUILDER_REVISION`, e.g., `6.0.0-v1.7.0-v1.0.0`.

where:

- `$CAPELLA_VERSION` is the semantic Capella version, e.g., `6.0.0` or `5.2.0`
- `$CAPELLA_DOCKER_IMAGES_REVISION` is the revision of this Github repository.

  - Any branch or tag name is supported as revision
  - All characters matching the regex `[^a-zA-Z0-9.]` will be replaces with `-`

- `$GITLAB_IMAGE_BUILDER_REVISION` is the revision of the Gitlab repository, where the Gitlab CI template is included.

  - We use the [predefined Gitlab CI variable](https://docs.gitlab.com/ee/ci/variables/predefined_variables.html) `$CI_COMMIT_REF_NAME` to determine the name of the branch or tag.
  - This part can be used for your own versioning, e.g., when you have to patch the Capella archives, but the semantic version is still the same.

In addition, you have to add the following environment variables on repository level.
Make sure to enable the "Expand variable reference" flag.

- `CAPELLA_DOCKER_IMAGES_REVISION`: Revision of this Github repository.
- `UID_ENV`: The user ID which will be used for the technical user.
- Variables related to the Docker registry (all parameters are passed to `docker login`):
  - `DOCKER_REGISTRY`: The URL to the Docker registry
  - `DOCKER_REGISTRY_USER`: Username of a techuser with push permission to the Docker registry
  - `DOCKER_REGISTRY_PASSWORD`: Corresponding password of the techuser

The tree inside of your Gitlab repository should look like:

```zsh
├── 5.0.0
│   ├── capella.tar.gz
│   ├── dropins
│   ├── ease
│   └── updateSite
├── 5.2.0
│   ├── capella.tar.gz
│   ├── dropins
│   ├── ease
│   └── updateSite
├── 6.0.0
│   ├── capella.tar.gz
│   ├── dropins
│   ├── ease
│   └── updateSite
├── libs
│   ├── libicu66_66.1-2ubuntu2_amd64.deb
│   ├── libjavascriptcoregtk-4.0-18_2.28.1-1_amd64.deb
│   ├── libjpeg-turbo8_2.0.3-0ubuntu1.20.04.1_amd64.deb
│   ├── libjpeg8_8c-2ubuntu8_amd64.deb
│   └── libwebkit2gtk-4.0-37_2.28.1-1_amd64.deb
└── pure-variants
    ├── dependencies
    └── updateSite
```

This is the minimal configuration. For more advanced configuration options,
please refer to the [Gitlab CI template](./image-builder.yml).

## Model validation

Currently, the model validation does NOT support:

- Loading of Capella libraries (only Capella projects without libraries are supported)
- Usage of subdirectories with the `$ENTRYPOINT`. The `.aird`-file has to be located in the root directory of the repository.
- Projects without `.project`-file. The `.project` has to be located in the root directory of the repository.

Please add the following section to your `.gitlab-ci.yml`:

```yml
variables:
  CAPELLA_VERSION: 6.0.0 # Enter the Capella version of the model here, only versions >= 6.0.0 are supported
  ENTRYPOINT: test.aird # Filename of the `.aird` file

include:
  - remote: https://raw.githubusercontent.com/DSD-DBS/capella-dockerimages/${CAPELLA_DOCKER_IMAGES_REVISION}/ci-templates/gitlab/model-validation.yml
```

For more information, please refer to the [Gitlab CI template](./model-validation.yml).
