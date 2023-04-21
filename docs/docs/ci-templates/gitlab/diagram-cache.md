<!--
 ~ SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Diagram cache

Please add the following section to your `.gitlab-ci.yml`:

```yaml
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
please refer to the [Gitlab CI template](https://github.com/DSD-DBS/capella-dockerimages/blob/main/ci-templates/gitlab/diagram-cache.yml).
