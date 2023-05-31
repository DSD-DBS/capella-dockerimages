<!--
 ~ SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Image builder

The image builder template builds all images supported by this repository, executes our tests on each builded images,
and pushes them to any Docker registry. We use it in our automated deployment environment for our [Collaboration project](https://github.com/DSD-DBS/capella-collab-manager).
We have restricted internet access in our build environment, so the Gitlab CI is optimized for restricted network access.

Please add the following section to your `.gitlab-ci.yml`:

```yaml
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
- `ENVIRONMENT`: Specifies the environment. In addition, you need to have the following variables for each environment:
  - `UID_${ENVIRONMENT}`: The user ID which will be used for the technical user.
  - Variables related to the Docker registry (all parameters are passed to `docker login`):
    - `DOCKER_REGISTRY_${ENVIRONMENT}`: The URL to the Docker registry
    - `DOCKER_REGISTRY_USER_${ENVIRONMENT}`: Username of a techuser with push permission to the Docker registry
    - `DOCKER_REGISTRY_PASSWORD_${ENVIRONMENT}`: Corresponding password of the techuser
- `T4C_SERVER_REGISTRY`: Docker registry which contains the required t4c server image
- `T4C_SERVER_TAG`: Docker tag that is used for the t4c server image
- `T4C_SERVER_TEST_DATA_REPO`: Link to a Git repository containing t4c test data needed to run the backup tests.
  The repository needs to have the following structure: `/data/$CAPELLA_VERSION/repositories/test-repo`
- `LOCAL_GIT_BASE_IMAGE`: Specifies the base image which is used to build the local git server for the pytest.

The tree inside of your Gitlab repository should look like:

```zsh
├── capella
│   ├── libs
│   │   ├── libicu66_66.1-2ubuntu2_amd64.deb
│   │   ├── libjavascriptcoregtk-4.0-18_2.28.1-1_amd64.deb
│   │   ├── libjpeg-turbo8_2.0.3-0ubuntu1.20.04.1_amd64.deb
│   │   ├── libjpeg8_8c-2ubuntu8_amd64.deb
│   │   └── libwebkit2gtk-4.0-37_2.28.1-1_amd64.deb
│   └── versions
│       ├── 5.0.0
│       │   ├── capella.tar.gz
│       │   ├── dropins
│       │   ├── ease
│       │   └── updateSite
│       ├── 5.2.0
│       │   ├── capella.tar.gz
│       │   ├── dropins
│       │   ├── ease
│       │   └── updateSite
│       ├── 6.0.0
│       │   ├── capella.tar.gz
│       │   ├── dropins
│       │   ├── ease
│       │   └── updateSite
│       └── 6.1.0
│           ├── capella.tar.gz
│           ├── dropins
│           ├── ease
│           └── updateSite
└── pure-variants
    ├── dependencies
    └── updateSite
```

This is the minimal configuration. For more advanced configuration options,
please refer to the [Gitlab CI template](https://github.com/DSD-DBS/capella-dockerimages/blob/main/ci-templates/gitlab/image-builder.yml).
