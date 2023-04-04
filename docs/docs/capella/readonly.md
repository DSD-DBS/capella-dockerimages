<!--
 ~ SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Capella read-only

<!-- prettier-ignore -->
!!! info
    The Docker image name for this image is `capella/readonly`

The read-only image builds on top of the Capella EASE remote image and provides support for the read-only use of models.

It clones a git repositories and automatically injects the cloned models in the workspace.

## Use the prebuilt image

```
docker run ghcr.io/dsd-dbs/capella-dockerimages/capella/readonly:$TAG
```

where `$TAG` is the Docker tag. For more information, have a look at our [tagging schema](introduction.md#tagging-schema-for-prebuilt-images).
Please check the [`Run the container`](#run-the-container) section to get an overview over environment variables you have to set during startup.

## Build it yourself

### Build it manually with Docker

To build the image, please run:

```zsh
docker build -t capella/readonly \
    --build-arg BASE_IMAGE=capella/ease/remote \
    readonly
```

## Run the container

There are two options available for read-only containers.
The first option supports multiple repositories, but you need to JSON-serizalize it.
With the second option, you can provide the details as environment variables directly.

Running the Capella read-only container is analogous to the Capella base container. Please run the [instructions of the Capella base container](../base.md#run-the-container), but add the `$EASE_LOG_LOCATION` environment variable during `docker run` (optional). The value should be the absolute path to log file. Defaults to `/proc/1/fd/1` (Docker logs) if not provided.

In addition, choose one of the following two options and consider the differences.

### Provide repository details as JSON

With this option, any number of Git models can be loaded.
These must first be serialized to JSON in the following format:

```json
[
  {
    "url": "https://github.com/DSD-DBS/py-capellambse.git", # Path that is used by 'git clone'
    "revision": "master",
    "depth": 1, # Optional: If depth == 0, the whole history is cloned. Defaults to 0
    "entrypoint": "tests/data/melodymodel/5_2/Melody Model Test.aird", # Path to the aird file, starting from the root of the repository
    "nature": "project", # Optional: Can be either 'project' or 'library'. Defaults to 'project'
    "username": "testuser", # Optional: Only need if repository access is restricted
    "password": "token" # Optional: Only need if repository access is restricted
  }
]
```

The JSON string has to be provided as value to the environment variable with the key `GIT_REPOS_JSON`:

```zsh
    -e GIT_REPOS_JSON=$GIT_REPOS_JSON
```

Please replace the `GIT_REPOS_JSON` with the JSON-string (described above).

### Provide repository details in separate environment variables

With this option, you can only provide details for exactly one repository at time.
If you want to make any number of models available, please use option [`Provide repository details as JSON`](#provide-repository-details-as-json).

Add this section to your `docker run` command:

```zsh
    -e GIT_URL=$GIT_URL \
    -e GIT_ENTRYPOINT=$GIT_ENTRYPOINT \
    -e GIT_REVISION=$GIT_REVISION \
    -e GIT_DEPTH=$GIT_DEPTH \
    -e GIT_USERNAME=$GIT_USERNAME \
    -e GIT_PASSWORD=$GIT_PASSWORD
```

Please replace the followings variables (in addition to the general variables):

- `$GIT_URL` with the URL to the Git repository. All URI-formats supported by the `git clone` command will work. Please do NOT include credentials in the URL as they will be not cleaned after cloning the model. You can provide HTTP credentials via the `GIT_USERNAME` and `GIT_PASSWORD` variables (see below).
- `$GIT_ENTRYPOINT` with the relative path from the root of your repository to the `aird`-file of your model, e.g. `path/to/model.aird`.
- `$GIT_REVISION` with the desired revision of the git repository. The revision is cloned with the `--single-branch` option, therefore only the specific revision is accessible. Only tags and branches are supported, commit hashes are NOT supported. If empty, the whole repository gets cloned.
- `$GIT_DEPTH` with the desired git depth. If not provided, the whole history will be cloned.
- `$GIT_USERNAME` with the git username if the repository is access protected. Leave empty, when no authentication is required.
- `$GIT_PASSWORD` with the git password if the repository is access protected. Leave empty, when no authentication is required. The password gets cleaned after cloning and is not accessible in the RDP connection.
