<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Image Builder

The image builder template builds all images supported by this repository,
executes our tests on each builded images, and pushes them to any Docker
registry. We use it in our automated deployment environment for our
[Collaboration project](https://github.com/DSD-DBS/capella-collab-manager).

## Setup

### SOPS Configuration

We use [SOPS](https://github.com/getsops/sops) to encrypt the configuration
file in the repository. To set up SOPS, you have to create a private key first:
[Generate a private GPG key](https://docs.github.com/en/authentication/managing-commit-signature-verification/generating-a-new-gpg-key)

### Gitlab Runner Configuration

To use the CI template, a few changes have to be made to the Gitlab runner:

```yaml title="config.toml"
[[runners]]
[runners.docker]
volumes = [
    "/shared:/shared", # (1)!
    "/builds:/builds", # (2)!
    "/var/run/docker.sock:/var/run/docker.sock", # (3)!
    "<host-path-to-private-key>:/secrets/private.gpg", # (4)!
]
```

1. In order to make optimal use of caching, we have to save the tag of the last
   built image. Since the Gitlab CI cache is not shared between concurrent
   runners, we use a shared volume `/shared`.
2. Expose `/builds` to the host, so that we can mount it to the build context.
3. The pack CLI needs access to the Docker daemon.
4. The previously generated private GPG key has to be mounted to the runner in
   order to decrypt the configuration file.

### Gitlab Repository Configuration

1.  Create a new repository where you'll store the archives of the tools.
1.  Set the CI/CD variable `CAPELLA_DOCKER_IMAGES_REVISION` on a repository
    level. The value can be any revision of this GitHub repository (we
    recommend `main`)
1.  In the new repository, add a `.gitlab-ci.yml` and include our build
    template:

    ```yaml title=".gitlab-ci.yml"
    include:
      - remote: https://raw.githubusercontent.com/DSD-DBS/capella-dockerimages/${CAPELLA_DOCKER_IMAGES_REVISION}/ci-templates/gitlab/image-builder.yml
    ```

1.  Add the SOPS configuration to the repository. Add the GPG fingerprints of
    all users who should be able to access the encrypted configuration file.

    ```yaml title=".sops.yaml"
    creation_rules:
      - path_regex: .*
        encrypted_regex: '^(password|token)$'
        key_groups:
          - pgp:
              - <gpg-fingerprint-of-runner>
              - <gpg-fingerprint-of-other-users>
    ```

1.  Create an encrypted file using SOPS `sops config.yml`. Add the following
    content:

    ```yaml title="config.yml"
    t4c-server:
      registry: 'https://example.com'
      tag: '$CAPELLA_VERSION-main' # (1)!
      test-data-repository: '' # (2)!

    registries: # (3)!
      xpra: 'https://xpra.org'
      eclipse: 'https://download.eclipse.org'

    base-images:
      debian: 'debian:bookworm'
      alpine: 'alpine:latest'

    architecture: amd64 # (4)!

    environments:
      staging:
        uid: 1001
        registry:
          url: 'https://registry.gitlab.com'
          user: username
          password: password
      production: ...
      development: ...
    ```

    1. Environment variables are resolved by the CI.
    2. Link to a Gitlab repository (relative to ) containing TeamForCapella
       test data needed to run the backup tests. The repository needs to have
       the following structure: `/data/$CAPELLA_VERSION/repositories/test-repo`
    3. Can be used to use custom registries / mirrors in restricted internet
       access.
    4. Build images for `amd64` or `arm64`.

1.  Add all required archives to the repository. The repository structure
    should look like:
    ```zsh
    ├── capella
    │   └── versions
    │       ├── 5.0.0
    │       │   ├── capella.tar.gz
    │       │   ├── dropins
    │       │   └── updateSite
    │       ├── 5.2.0
    │       │   ├── capella.tar.gz
    │       │   ├── dropins
    │       │   └── updateSite
    │       ├── 6.0.0
    │       │   ├── capella.tar.gz
    │       │   ├── dropins
    │       │   └── updateSite
    │       └── 6.1.0
    │           ├── capella.tar.gz
    │           ├── dropins
    │           └── updateSite
    ├── papyrus
    │   └── versions
    │       └── 6.4.0
    │           └── papyrus.tar.gz
    ├─── pure-variants
    │   └── updateSite
    ├── .gitlab-ci.yml
    ├── .sops.yml
    └── config.yml
    ```

## Tagging of Images

### Capella

The resulting Capella based images will be tagged in the following format:
`$CAPELLA_VERSION-$CAPELLA_DOCKER_IMAGES_REVISION-$GITLAB_IMAGE_BUILDER_REVISION`,
e.g., `6.0.0-v1.7.0-v1.0.0`.

where:

- `$CAPELLA_VERSION` is the semantic Capella version, e.g., `6.0.0` or `5.2.0`
- `$CAPELLA_DOCKER_IMAGES_REVISION` is the revision of this Github repository.

  - Any branch or tag name is supported as revision
  - All characters matching the regex `[^a-zA-Z0-9.]` will be replaces with `-`

- `$GITLAB_IMAGE_BUILDER_REVISION` is the revision of the Gitlab repository,
  where the Gitlab CI template is included.

  - We use the
    [predefined Gitlab CI variable](https://docs.gitlab.com/ee/ci/variables/predefined_variables.html)
    `$CI_COMMIT_REF_NAME` to determine the name of the branch or tag.
  - This part can be used for your own versioning, e.g., when you have to patch
    the Capella archives, but the semantic version is still the same.

### Papyrus

The resulting Papyrus based images will be tagged in the following format:
`$PAPYRUS_VERSION-$CAPELLA_DOCKER_IMAGES_REVISION-$GITLAB_IMAGE_BUILDER_REVISION`,
e.g., `6.4.0-v1.7.0-v1.0.0`.
