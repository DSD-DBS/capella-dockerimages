<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Cleanup

## Overview

The `cleanup` template is designed to address the issue of legacy or
remaining Docker containers resulting from a canceled or timed-out pipeline in the GitLab CI/CD workflow.
It provides a mechanism to clean up test Docker containers to ensure a clean and consistent environment for subsequent pipeline runs.

## Usage

To use the `cleanup` template, you need to include the template in your `.gitlab-ci.yml`:

```yaml
include:
  - remote: https://raw.githubusercontent.com/DSD-DBS/capella-dockerimages/${CAPELLA_DOCKER_IMAGES_REVISION}/ci-templates/gitlab/cleanup.yml
```

This template supports the following variables:

- `CLEANUP`:
  - Description: Controls the cleanup behavior for test Docker containers.
  - Allowed values:
    - `0` (default): Do not clean up test Docker containers.
    - `1`: Clean up test Docker containers.

## Functionality

The `cleanup` template implements a specific logic to remove test Docker containers
based on their labels. This logic ensures that any containers labeled with `capella-dockerimages-pytest-container=true`
are stopped and removed.

### Script

The template script performs the following actions:

1. Retrieves the IDs of the test Docker containers labeled with `capella-dockerimages-pytest-container=true`.
2. If any test containers are found:
   - Stops the containers using the `docker stop` command.
   - Removes the containers using the `docker rm` command.
3. If no test containers are found, the script exits with a status of `0`.

### Note

This template serves as a workaround until GitLab introduces proper cleanup functionality for unsuccessful job cases (i.e., `after_script`).
You can monitor the progress of this feature in the following GitLab issue: [https://gitlab.com/gitlab-org/gitlab/-/issues/387230](https://gitlab.com/gitlab-org/gitlab/-/issues/387230).
