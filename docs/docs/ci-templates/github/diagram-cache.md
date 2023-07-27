<!--
 ~ SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Diagram cache

Please add the following section to your `.github/workflows/diagram-cache.yml`:

```yaml
name: update_capella_diagram_cache

on: push

jobs:
  update_capella_diagram_cache:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      - name: Generate and upload diagram cache
        uses: DSD-DBS/capella-dockerimages/ci-templates/github/diagram-cache@main
        with:
          entry_point: test/test.aird # Relative entrypoint to .aird file inside repository (starting from the root of the repository).
```

This is the minimal configuration, specifying only the `entry_point`. Nevertheless, there
are several other options to configure your diagram cache workflow.
For more options please have a look at the possible [inputs](https://github.com/DSD-DBS/capella-dockerimages/blob/main/ci-templates/github/diagram-cache.yml)
