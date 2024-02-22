<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Build Capella from source

We provide a script, which runs a Docker container to build Capella from
source. Our builder script adds the aarch64 build platform for macOS and linux.
Please note that Capella itself has no official support for the aarch64
architecture yet. We can not guarantee that everything works, but all of the
official Capella tests passed on the generated archives.

In addition, the builder only works for Capella version 6.0.0 for now. To start
the script, please run:

```
CAPELLA_VERSION=6.0.0 make capella/builder
```

When the script is successful, you should see the result in `builder/output`.

We store a cache of the maven repository in the `builder/m2_cache` directory.
If you don't need the cache anymore, you can delete the directory after
building.
