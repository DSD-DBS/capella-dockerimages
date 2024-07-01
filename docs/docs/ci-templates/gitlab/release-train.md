<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Release train

The image builder Gitlab CI/CD template is limited to one environment and one
Capella version. In addition, we provide a release train template, which can be
used to trigger the image builder pipeline with a matrix of Capella versions
and environments.

!!! warning

    To continue, create a new image builder Gitlab repository and follow the instuctions of the image builder template.

The pipeline is not triggered automatically. There are a few options to trigger
the pipeline automatically:

For changes on Github in this repository (e.g., new push to branches or a new
tag):

- If you're using the PREMIUM version of Gitlab, pipelines can be automatically
  triggered for external repositories:
  https://docs.gitlab.com/ee/ci/ci_cd_for_external_repos/
- Detect changes on the remote with `git ls-remote` and trigger a Gitlab CI
  pipeline with a cronjob.

For changes in your Gitlab image builder repository:

- Use a [Gitlab trigger](https://docs.gitlab.com/ee/ci/yaml/#trigger) to
  trigger the release train pipeline.

You can customize the pipeline to your needs (e.g., define multiple
environments). The template provides three different jobs `.base`, `.capella`
and `.jupyter` which can be extended:

```yaml
include:
  - remote: https://raw.githubusercontent.com/DSD-DBS/capella-dockerimages/${CAPELLA_DOCKER_IMAGES_REVISION}/ci-templates/gitlab/release-train.yml"

.staging: &staging
  rules:
    # For commits on the main branch, build for the staging environment
    - if: '$CI_COMMIT_REF_NAME == "main"'
    - when: manual
  variables:
    ENVIRONMENT: staging
    CAPELLA_DOCKER_IMAGES_REVISION: '$CI_COMMIT_REF_NAME'
    IMAGE_BUILDER_GITLAB_REPOSITORY: '$IMAGE_BUILDER_GITLAB_REPOSITORY'
    BUILD_FOR_LATEST_TAG: '0'

.production: &production
  rules:
    # For tags, build for the production environment
    - if: '$CI_COMMIT_TAG != null'
  variables:
    ENVIRONMENT: production
    CAPELLA_DOCKER_IMAGES_REVISION: '$CI_COMMIT_REF_NAME'
    IMAGE_BUILDER_GITLAB_REPOSITORY: '$IMAGE_BUILDER_GITLAB_REPOSITORY'
    BUILD_FOR_LATEST_TAG: '1'

production-base:
  extends: .base
  <<: *production

production-jupyter:
  extends: .jupyter
  needs:
    - job: production-base
      optional: true
  <<: *production

production-capella:
  extends: .capella
  needs:
    - job: production-base
      optional: true
  <<: *production

staging-base:
  extends: .base
  <<: *staging

staging-jupyter:
  extends: .jupyter
  needs:
    - job: staging-base
      optional: true
  <<: *staging

staging-capella:
  extends: .capella
  needs:
    - job: staging-base
      optional: true
  <<: *staging
```
