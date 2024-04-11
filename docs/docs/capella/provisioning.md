<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Load models to your workspace automatically

!!! info "Migration from `v1.X.X` to `v2.X.X` and later"

    This feature replaces the read-only image of version `v1.X.X`.
    Before starting the new image, you have to clone the Git repositories
    that you've passed to the read-only image manually. The path with all
    repositories can then be mounted to the new image as described below.

To load models to your workspace automatically, you can mount a volume to the
container.

```
docker run -d \
    -v path/to/models/on/host:/models \
    -e ECLIPSE_PROJECTS_TO_LOAD='[]' \
    capella/base
```

The `ECLIPSE_PROJECTS_TO_LOAD` environment variable is a JSON array that
contains:

```json
[
  {
    "revision": "master", // (1)
    "nature": "project", // (2)
    "path": "/models/directory", // (3)
    "entrypoint": "test.aird" // (4)
  }
]
```

1. The revision of the Eclipse project. In case of duplicated project names,
   the revision is added as suffix to the project name.
2. Optional: Can be either 'project' or 'library'. Defaults to 'project'.
   Ignored if the the directory provided in the `path` attribute contains a
   `.project` file.
3. Path to the directory where the project should be loaded from.
4. Path to the aird file, starting from the directory provided in the `path`
   attribute. Required if the `.aird` is not placed directly in the directory
   provided as `path`. If None, the aird is searched in the path directory
   without recursion.

All additional attributes are ignored.

You can use all images that are based on the `capella/base` image for this
feature.
