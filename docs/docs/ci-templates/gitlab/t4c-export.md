<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Export to T4C

Please add the following section to your `.gitlab-ci.yml`:

```yaml
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

In addition, you have to add the following environment variables on repository
level. Make sure to enable the "Expand variable reference" flag.

- `CAPELLA_DOCKER_IMAGES_REVISION`: Revision of this Github repository
- `HTTP_LOGIN` and `HTTP_PASSWORD`: Username / password for the T4C REST API
- `T4C_USERNAME` and `T4C_PASSWORD`: Username / password for the T4C repository

This is the minimal configuration. For more advanced configuration options,
please refer to the
[Gitlab CI template](https://github.com/DSD-DBS/capella-dockerimages/blob/main/ci-templates/gitlab/exporter.yml).
