<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Migration from v2.0.0 to v3.0.0

- The `capella_loop.sh` and `CAPELLA_VERSIONS` environment variables were
  dropped. To build images for different Capella versions, the the Make target
  multiple times with different `CAPELLA_VERSION` environment variables.
- Bulidpacks is required as new dependency.
- The `t4c/client/base`, `t4c/client/remote`,
  `t4c/client/remote/pure-variants`, `capella/remote/pure-variants`,
  `eclipse/remote/pure-variants`, `eclipse/remote`, `capella/remote` and
  `papyrus/remote` were removed. The other targets don't have the suffix
  `/base` anymore. Instead, there are only the `capella`, `papyrus`, `eclipse`
  and `jupyter` targets. The `t4c` and `pure-variants` extensions are
  automatically installed if the archives are placed in the correct location.
  Remote support is automatically added to the image. To disable it, set
  `REMOTE_CONNECTION_SUPPORT=0`.
- The `builder` target was removed. It can be still accessed in the Git
  history, but is no longer maintained.
