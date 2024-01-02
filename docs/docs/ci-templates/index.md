<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# CI/CD templates

## Gitlab CI/CD

Currently, we provide the following Gitlab CI/CD templates:

- [Export to T4C](./gitlab/t4c-export.md): Export model in repository to T4C using the merge strategy
- [Diagram cache](./gitlab/diagram-cache.md): Export diagrams of a Capella model and store them in Gitlab artifacts
- [Image builder](#image-builder): Build and push all Docker images to any Docker registry.
- [Model validation](#model-validation): Runs the Capella model validation CLI tool.

And the following Github CI/CD actions:

- [Diagram cache](./github/diagram-cache.md): Export diagrams of a Capella model and store them in Github artifacts,
  with the option to push it to a new branch

We offer more templates as part of our `py-capellambse` project. Please have a look [here](https://github.com/DSD-DBS/py-capellambse/tree/master/ci-templates/gitlab).
