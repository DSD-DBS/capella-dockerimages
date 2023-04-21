<!--
 ~ SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Model validation

Currently, the model validation does NOT support:

- Loading of Capella libraries (only Capella projects without libraries are supported)
- Usage of subdirectories with the `$ENTRYPOINT`. The `.aird`-file has to be located in the root directory of the repository.
- Projects without `.project`-file. The `.project` has to be located in the root directory of the repository.

Please add the following section to your `.gitlab-ci.yml`:

```yaml
variables:
  CAPELLA_VERSION: 6.0.0 # Enter the Capella version of the model here, only versions >= 6.0.0 are supported
  ENTRYPOINT: test.aird # Filename of the `.aird` file

include:
  - remote: https://raw.githubusercontent.com/DSD-DBS/capella-dockerimages/${CAPELLA_DOCKER_IMAGES_REVISION}/ci-templates/gitlab/model-validation.yml
```

For more information, please refer to the [Gitlab CI template](https://github.com/DSD-DBS/capella-dockerimages/blob/main/ci-templates/gitlab/model-validation.yml).
