# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

# Add prefix to all dockerimage names, e.g. capella-collab
export DOCKER_PREFIX ?=

# T4C license secret (usually a long numeric string)
T4C_LICENCE_SECRET ?= XXX

# Predefined T4C repositories (comma separated), e.g. testrepo,testrepo2
T4C_REPOSITORIES ?= testrepo

# T4C server host
T4C_SERVER_HOST ?= host.docker.internal

# T4C server port
T4C_SERVER_PORT ?= 2036

# Predefined T4C username
T4C_USERNAME ?= admin

# T4C password
T4C_PASSWORD ?= admin

# Remote container rdp password
RMT_PASSWORD ?= tmp_passwd2

# Git repository url for the importer, e.g. https://github.com/example.git
GIT_REPO_URL ?= http://host.docker.internal:$(GIT_SERVER_PORT)/git/git-test-repo.git

# Git repository branch for the importer, e.g. main
GIT_REPO_BRANCH ?= main

# Git entrypoint (path to aird file)
GIT_REPO_ENTRYPOINT ?= test.aird

# Git depth to clone
GIT_REPO_DEPTH ?= 0

# T4C repository name for the importer, e.g. repoCapella
T4C_IMPORTER_REPO ?= repoCapella

# T4C project name for the importer, e.g. project
T4C_IMPORTER_PROJECT ?= test

# Git username for the backup container to push changes
GIT_USERNAME ?= username

# Git password for the backup container to push changes
GIT_PASSWORD ?= password

# Preferred RDP port on your host system
RDP_PORT ?= 3390

# Subpath to serve the xpra client on
XPRA_SUBPATH ?= /xpra

# Port for direct access to the xpra htm5 server
# Only enabled in debug routes.
XPRA_DEBUG_PORT ?= 10001

CONNECTION_METHOD ?= xpra # xpra or xrdp

# External port for web-based containers
WEB_PORT ?= 8888

# Port for the Git Server which is used for debug purposes
# Can be used for manual testing of the importer and exporter.
GIT_SERVER_PORT ?= 10001

# Preferred metrics port on your host system
METRICS_PORT ?= 9118

# Capella version used for builds and tests
export CAPELLA_VERSIONS ?= 5.0.0 5.2.0 6.0.0 6.1.0

# Capella version used to run containers
export CAPELLA_VERSION ?= 6.1.0

# Workspace directory in volumes/workspaces, e.g. workspace for /volumes/workspaces/workspace
WORKSPACE_NAME ?= workspace

AUTOSTART_CAPELLA ?= 1

# Comma-separated list of dropins to download & add, doesn't affect copied & mounted dropins
# See available options in documentation: https://dsd-dbs.github.io/capella-dockerimages/capella/base/#optional-customisation-of-the-capella-client
CAPELLA_DROPINS ?= CapellaXHTMLDocGen,DiagramStyler,PVMT,Filtering,Requirements,SubsystemTransition,TextualEditor

# Only use when "capella_loop.sh" is NOT used
export DOCKER_TAG_SCHEMA ?= $$CAPELLA_VERSION-$$CAPELLA_DOCKERIMAGES_REVISION

PAPYRUS_VERSION ?= 6.4.0

ECLIPSE_VERSION ?= 4.27

# Should be 'latest', the branch name, the commit hash or a Git tag name
export CAPELLA_DOCKERIMAGES_REVISION ?= latest
export JUPYTER_NOTEBOOK_REVISION ?= python-3.11

PURE_VARIANTS_VERSION ?= 6.0.1

# UID which is used for the techuser in the Docker images
export TECHUSER_UID = 1004370000

# Capella build type (online/offline)
CAPELLA_BUILD_TYPE ?= online

# Old GTK versions can improve the Capella description editor experience.
# Set the option to 'false' if you want to run it on arm architectures.
INSTALL_OLD_GTK_VERSION ?= true

PURE_VARIANTS_LICENSE_SERVER ?= http://localhost:8080

# Inject libraries from the capella/libs directory
INJECT_LIBS_CAPELLA ?= false

# Build architecture: amd64 or arm64
BUILD_ARCHITECTURE ?= amd64

DOCKER_BUILD_FLAGS ?= --platform linux/$(BUILD_ARCHITECTURE)
DOCKER_RUN_FLAGS ?= --add-host=host.docker.internal:host-gateway --rm -it

# If set to 1, we will push the images to the specified registry
PUSH_IMAGES ?= 0

# Registry to push images
DOCKER_REGISTRY ?= localhost:12345

# Log level when running Docker containers
LOG_LEVEL ?= DEBUG

# If this option is set to 1, all tests that require a running t4c server
# will be executed. To run these tests, you need a Makefile in
# t4c/server with a target t4c/server/server that builds the t4c server
# docker images and provides them in the following format:
# t4c/server/server:x.x.x-latest. You also need test data in
# tests/t4c-server-test-data/data/x.x.x, which consists of a
# test repository (name test-repo) with a test project (name test-project).
# x.x.x here refers to the capella version
RUN_TESTS_WITH_T4C_SERVER ?= 0

# If this option is set to 1, all tests that require a t4c client will
# be executed. To run these tests, you must place the t4c files in the
# correct locations (as described in the README)
RUN_TESTS_WITH_T4C_CLIENT ?= 0

export DOCKER_BUILDKIT=1
export MAKE_CURRENT_TARGET=$@

.ONESHELL:
SHELL=/bin/bash

all: \
	base \
	jupyter-notebook \
	capella/base \
	capella/remote \
	t4c/client/base \
	t4c/client/remote \
	t4c/client/remote/pure-variants \
	capella/remote/pure-variants

base: SHELL=/bin/bash
base:
	docker build $(DOCKER_BUILD_FLAGS) \
		--build-arg UID=$(TECHUSER_UID) \
		-t $(DOCKER_PREFIX)$@:$(CAPELLA_DOCKERIMAGES_REVISION) \
		base
	$(MAKE) PUSH_IMAGES=$(PUSH_IMAGES) DOCKER_TAG=$(CAPELLA_DOCKERIMAGES_REVISION) IMAGENAME=$@ .push

jupyter-notebook: DOCKER_TAG=$(JUPYTER_NOTEBOOK_REVISION)
jupyter-notebook: base
	docker build $(DOCKER_BUILD_FLAGS) -t $(DOCKER_PREFIX)$@:$(DOCKER_TAG) jupyter-notebook
	$(MAKE) PUSH_IMAGES=$(PUSH_IMAGES) DOCKER_TAG=$(DOCKER_TAG) IMAGENAME=$@ .push

capella/base: SHELL=./capella_loop.sh
capella/base: base
	envsubst < capella/.dockerignore.template > capella/.dockerignore
	docker build $(DOCKER_BUILD_FLAGS) \
		-t $(DOCKER_PREFIX)$@:$$DOCKER_TAG \
		--build-arg BUILD_ARCHITECTURE=$(BUILD_ARCHITECTURE) \
		--build-arg BASE_IMAGE=$(DOCKER_PREFIX)$<:$(CAPELLA_DOCKERIMAGES_REVISION) \
		--build-arg BUILD_TYPE=$(CAPELLA_BUILD_TYPE) \
		--build-arg CAPELLA_VERSION=$$CAPELLA_VERSION \
		--build-arg "CAPELLA_DROPINS=$(CAPELLA_DROPINS)" \
		--build-arg "INJECT_PACKAGES=$(INJECT_LIBS_CAPELLA)" \
		--build-arg INSTALL_OLD_GTK_VERSION=$(INSTALL_OLD_GTK_VERSION) \
		capella
	rm capella/.dockerignore
	$(MAKE) PUSH_IMAGES=$(PUSH_IMAGES) IMAGENAME=$@ .push

papyrus/base: DOCKER_TAG=$(PAPYRUS_VERSION)-$(CAPELLA_DOCKERIMAGES_REVISION)
papyrus/base: DOCKER_BUILD_FLAGS=--platform linux/amd64
papyrus/base: base
	docker build $(DOCKER_BUILD_FLAGS) \
		-t $(DOCKER_PREFIX)$@:$(DOCKER_TAG) \
		--build-arg BASE_IMAGE=$(DOCKER_PREFIX)$<:$(CAPELLA_DOCKERIMAGES_REVISION) \
		--build-arg PAPYRUS_VERSION=$(PAPYRUS_VERSION) \
		papyrus
	$(MAKE) PUSH_IMAGES=$(PUSH_IMAGES) DOCKER_TAG=$(DOCKER_TAG) IMAGENAME=$@ .push

eclipse/base: DOCKER_TAG=$(ECLIPSE_VERSION)-$(CAPELLA_DOCKERIMAGES_REVISION)
eclipse/base: base
	docker build $(DOCKER_BUILD_FLAGS) \
		-t $(DOCKER_PREFIX)$@:$(DOCKER_TAG) \
		--build-arg BUILD_ARCHITECTURE=$(BUILD_ARCHITECTURE) \
		--build-arg BASE_IMAGE=$(DOCKER_PREFIX)$<:$(CAPELLA_DOCKERIMAGES_REVISION) \
		--build-arg ECLIPSE_VERSION=$(ECLIPSE_VERSION) \
		eclipse
	$(MAKE) PUSH_IMAGES=$(PUSH_IMAGES) DOCKER_TAG=$(DOCKER_TAG) IMAGENAME=$@ .push

capella/remote: SHELL=./capella_loop.sh
capella/remote: capella/base
	docker build $(DOCKER_BUILD_FLAGS) -t $(DOCKER_PREFIX)$@:$$DOCKER_TAG --build-arg BASE_IMAGE=$(DOCKER_PREFIX)$<:$$DOCKER_TAG remote
	$(MAKE) PUSH_IMAGES=$(PUSH_IMAGES) IMAGENAME=$@ .push

papyrus/remote: DOCKER_TAG=$(PAPYRUS_VERSION)-$(CAPELLA_DOCKERIMAGES_REVISION)
papyrus/remote: DOCKER_BUILD_FLAGS=--platform linux/amd64
papyrus/remote: papyrus/base
	docker build $(DOCKER_BUILD_FLAGS) \
		-t $(DOCKER_PREFIX)$@:$(DOCKER_TAG) \
		--build-arg BASE_IMAGE=$(DOCKER_PREFIX)$<:$(DOCKER_TAG) \
		remote
	$(MAKE) PUSH_IMAGES=$(PUSH_IMAGES) DOCKER_TAG=$(DOCKER_TAG) IMAGENAME=$@ .push

eclipse/remote: DOCKER_TAG=$(ECLIPSE_VERSION)-$(CAPELLA_DOCKERIMAGES_REVISION)
eclipse/remote: eclipse/base
	docker build $(DOCKER_BUILD_FLAGS) \
		-t $(DOCKER_PREFIX)$@:$(DOCKER_TAG) \
		--build-arg BASE_IMAGE=$(DOCKER_PREFIX)$<:$(DOCKER_TAG) \
		remote
	$(MAKE) PUSH_IMAGES=$(PUSH_IMAGES) DOCKER_TAG=$(DOCKER_TAG) IMAGENAME=$@ .push

eclipse/remote/pure-variants: DOCKER_TAG=$(ECLIPSE_VERSION)-$(PURE_VARIANTS_VERSION)-$(CAPELLA_DOCKERIMAGES_REVISION)
eclipse/remote/pure-variants: eclipse/remote
	docker build $(DOCKER_BUILD_FLAGS) \
		-t $(DOCKER_PREFIX)$@:$(DOCKER_TAG) \
		--build-arg BASE_IMAGE=$(DOCKER_PREFIX)$<:$(ECLIPSE_VERSION)-$(CAPELLA_DOCKERIMAGES_REVISION) \
		--build-arg PURE_VARIANTS_VERSION=$(PURE_VARIANTS_VERSION) \
		pure-variants
	$(MAKE) PUSH_IMAGES=$(PUSH_IMAGES) DOCKER_TAG=$(DOCKER_TAG) IMAGENAME=$@ .push

t4c/client/base: SHELL=./capella_loop.sh
t4c/client/base: capella/base
	envsubst < t4c/.dockerignore.template > t4c/.dockerignore
	docker build $(DOCKER_BUILD_FLAGS) -t $(DOCKER_PREFIX)$@:$$DOCKER_TAG --build-arg BASE_IMAGE=$(DOCKER_PREFIX)$<:$$DOCKER_TAG --build-arg CAPELLA_VERSION=$$CAPELLA_VERSION t4c
	rm t4c/.dockerignore
	$(MAKE) PUSH_IMAGES=$(PUSH_IMAGES) IMAGENAME=$@ .push

t4c/client/remote: SHELL=./capella_loop.sh
t4c/client/remote: t4c/client/base
	docker build $(DOCKER_BUILD_FLAGS) -t $(DOCKER_PREFIX)$@:$$DOCKER_TAG --build-arg BASE_IMAGE=$(DOCKER_PREFIX)$<:$$DOCKER_TAG remote
	$(MAKE) PUSH_IMAGES=$(PUSH_IMAGES) IMAGENAME=$@ .push

t4c/client/remote/pure-variants: SHELL=./capella_loop.sh
t4c/client/remote/pure-variants: t4c/client/remote
	docker build $(DOCKER_BUILD_FLAGS) \
		-t $(DOCKER_PREFIX)$@:$$DOCKER_TAG \
		--build-arg BASE_IMAGE=$(DOCKER_PREFIX)$<:$$DOCKER_TAG \
		--build-arg PURE_VARIANTS_VERSION=$(PURE_VARIANTS_VERSION) \
		pure-variants
	$(MAKE) PUSH_IMAGES=$(PUSH_IMAGES) IMAGENAME=$@ .push

capella/remote/pure-variants: SHELL=./capella_loop.sh
capella/remote/pure-variants: capella/remote
	docker build $(DOCKER_BUILD_FLAGS) -t $(DOCKER_PREFIX)$@:$$DOCKER_TAG --build-arg BASE_IMAGE=$(DOCKER_PREFIX)$<:$$DOCKER_TAG pure-variants
	$(MAKE) PUSH_IMAGES=$(PUSH_IMAGES) IMAGENAME=$@ .push

capella/builder:
	docker build $(DOCKER_BUILD_FLAGS) -t $(DOCKER_PREFIX)$@:$(CAPELLA_DOCKERIMAGES_REVISION) builder
	docker run -it -e CAPELLA_VERSION=$(CAPELLA_VERSION) -v $$(pwd)/builder/output/$(CAPELLA_VERSION):/output -v $$(pwd)/builder/m2_cache:/root/.m2/repository $(DOCKER_PREFIX)$@:$(CAPELLA_DOCKERIMAGES_REVISION)

run-capella/base: capella/base
	docker run $(DOCKER_RUN_FLAGS) \
		$(DOCKER_PREFIX)$<:$$(echo "$(DOCKER_TAG_SCHEMA)" | envsubst)

run-jupyter-notebook: jupyter-notebook
	docker run $(DOCKER_RUN_FLAGS) \
		-p $(WEB_PORT):8888 \
		-v $$(pwd)/volumes/workspace/notebooks:/tmp/notebooks \
		-e WORKSPACE_DIR=/tmp/notebooks \
		-e JUPYTER_BASE_URL=/ \
		$(DOCKER_PREFIX)$<:$(JUPYTER_NOTEBOOK_REVISION)

run-capella/remote: capella/remote
	FLAGS="";
	if [ -n "$(WORKSPACE_NAME)" ]; then \
		FLAGS="-v $$(pwd)/volumes/workspaces/$(WORKSPACE_NAME):/workspace"; \
	fi
	docker run $(DOCKER_RUN_FLAGS) \
		$$FLAGS \
		-e RMT_PASSWORD=$(RMT_PASSWORD) \
		-e CONNECTION_METHOD=$(CONNECTION_METHOD) \
		-e AUTOSTART_CAPELLA=$(AUTOSTART_CAPELLA) \
		-e XPRA_SUBPATH=$(XPRA_SUBPATH) \
		-p $(RDP_PORT):3389 \
		-p $(WEB_PORT):10000 \
		-p $(METRICS_PORT):9118 \
		$(DOCKER_PREFIX)$<:$$(echo "$(DOCKER_TAG_SCHEMA)" | envsubst)

run-papyrus/remote: DOCKER_TAG=$(PAPYRUS_VERSION)-$(CAPELLA_DOCKERIMAGES_REVISION)
run-papyrus/remote: papyrus/remote
	docker run \
		--platform linux/amd64 \
		-e RMT_PASSWORD=$(RMT_PASSWORD) \
		-e CONNECTION_METHOD=$(CONNECTION_METHOD) \
		-e XPRA_SUBPATH=$(XPRA_SUBPATH) \
		-p $(RDP_PORT):3389 \
		-p $(WEB_PORT):10000 \
		-p $(METRICS_PORT):9118 \
		$(DOCKER_PREFIX)$<:$(DOCKER_TAG)

run-eclipse/remote: DOCKER_TAG=$(ECLIPSE_VERSION)-$(CAPELLA_DOCKERIMAGES_REVISION)
run-eclipse/remote: eclipse/remote
	docker run \
		-e RMT_PASSWORD=$(RMT_PASSWORD) \
		-e CONNECTION_METHOD=$(CONNECTION_METHOD) \
		-e XPRA_SUBPATH=$(XPRA_SUBPATH) \
		-p $(RDP_PORT):3389 \
		-p $(WEB_PORT):10000 \
		-p $(METRICS_PORT):9118 \
		$(DOCKER_PREFIX)$<:$(DOCKER_TAG)

run-eclipse/remote/pure-variants: DOCKER_TAG=$(ECLIPSE_VERSION)-$(PURE_VARIANTS_VERSION)-$(CAPELLA_DOCKERIMAGES_REVISION)
run-eclipse/remote/pure-variants: eclipse/remote/pure-variants
	docker run $(DOCKER_RUN_FLAGS) \
		-e RMT_PASSWORD=$(RMT_PASSWORD) \
		-e PURE_VARIANTS_LICENSE_SERVER=$(PURE_VARIANTS_LICENSE_SERVER) \
		-e CONNECTION_METHOD=$(CONNECTION_METHOD) \
		-e XPRA_SUBPATH=$(XPRA_SUBPATH) \
		-v $$(pwd)/volumes/pure-variants:/inputs/pure-variants \
		-v $$(pwd)/volumes/workspace:/workspace \
		-v $$(pwd)/pure-variants/versions:/opt/versions \
		-p $(RDP_PORT):3389 \
		-p $(WEB_PORT):10000 \
		-p $(METRICS_PORT):9118 \
		$(DOCKER_PREFIX)$<:$(DOCKER_TAG)


run-t4c/client/remote-legacy: t4c/client/remote
	docker run $(DOCKER_RUN_FLAGS) \
		-v $$(pwd)/volumes/workspaces/$(WORKSPACE_NAME):/workspace \
		-e T4C_LICENCE_SECRET=$(T4C_LICENCE_SECRET) \
		-e T4C_SERVER_HOST=$(T4C_SERVER_HOST) \
		-e T4C_SERVER_PORT=$(T4C_SERVER_PORT) \
		-e T4C_REPOSITORIES=$(T4C_REPOSITORIES) \
		-e RMT_PASSWORD=$(RMT_PASSWORD) \
		-e T4C_USERNAME=$(T4C_USERNAME) \
		-e CONNECTION_METHOD=$(CONNECTION_METHOD) \
		-e XPRA_SUBPATH=$(XPRA_SUBPATH) \
		-p $(RDP_PORT):3389 \
		-p $(WEB_PORT):10000 \
		-p $(METRICS_PORT):9118 \
		$(DOCKER_PREFIX)$<:$$(echo "$(DOCKER_TAG_SCHEMA)" | envsubst)

run-t4c/client/remote: t4c/client/remote
	docker run $(DOCKER_RUN_FLAGS) \
		-v $$(pwd)/volumes/workspaces/$(WORKSPACE_NAME):/workspace \
		-e T4C_LICENCE_SECRET=$(T4C_LICENCE_SECRET) \
		-e T4C_JSON=$(T4C_JSON) \
		-e RMT_PASSWORD=$(RMT_PASSWORD) \
		-e T4C_USERNAME=$(T4C_USERNAME) \
		-e CONNECTION_METHOD=$(CONNECTION_METHOD) \
		-e XPRA_SUBPATH=$(XPRA_SUBPATH) \
		-p $(RDP_PORT):3389 \
		-p $(WEB_PORT):10000 \
		-p $(METRICS_PORT):9118 \
		$(DOCKER_PREFIX)$<:$$(echo "$(DOCKER_TAG_SCHEMA)" | envsubst)

run-t4c/client/remote/pure-variants: t4c/client/remote/pure-variants
	docker run $(DOCKER_RUN_FLAGS) \
		-e T4C_LICENCE_SECRET=$(T4C_LICENCE_SECRET) \
		-e T4C_JSON=$(T4C_JSON) \
		-e RMT_PASSWORD=$(RMT_PASSWORD) \
		-e T4C_USERNAME=$(T4C_USERNAME) \
		-e PURE_VARIANTS_LICENSE_SERVER=$(PURE_VARIANTS_LICENSE_SERVER) \
		-v $$(pwd)/volumes/pure-variants:/inputs/pure-variants \
		-v $$(pwd)/volumes/workspace:/workspace \
		-e AUTOSTART_CAPELLA=$(AUTOSTART_CAPELLA) \
		-e CONNECTION_METHOD=$(CONNECTION_METHOD) \
		-e XPRA_SUBPATH=$(XPRA_SUBPATH) \
		-p $(RDP_PORT):3389 \
		-p $(WEB_PORT):10000 \
		-p $(METRICS_PORT):9118 \
		$(DOCKER_PREFIX)$<:$$(echo "$(DOCKER_TAG_SCHEMA)" | envsubst)


run-t4c/client/backup: t4c/client/base
	docker run $(DOCKER_RUN_FLAGS) --rm -it \
		-e GIT_REPO_URL="$(GIT_REPO_URL)" \
		-e GIT_REPO_BRANCH="$(GIT_REPO_BRANCH)" \
		-e T4C_REPO_HOST="$(T4C_SERVER_HOST)" \
		-e T4C_REPO_PORT="$(T4C_SERVER_PORT)" \
		-e T4C_REPO_NAME="$(T4C_IMPORTER_REPO)" \
		-e T4C_PROJECT_NAME="$(T4C_IMPORTER_PROJECT)" \
		-e T4C_USERNAME="$(T4C_USERNAME)" \
		-e T4C_PASSWORD="$(T4C_PASSWORD)" \
		-e GIT_USERNAME="$(GIT_USERNAME)" \
		-e GIT_PASSWORD="$(GIT_PASSWORD)" \
		-e LOG_LEVEL="$(LOG_LEVEL)" \
		$(DOCKER_PREFIX)$<:$$(echo "$(DOCKER_TAG_SCHEMA)" | envsubst) backup

run-t4c/client/backup-local: t4c/client/base
	docker run $(DOCKER_RUN_FLAGS) --rm -it \
		-v $$(pwd)/volumes/backup:/tmp/model \
		-e FILE_HANDLER=local \
		-e T4C_REPO_HOST="$(T4C_SERVER_HOST)" \
		-e T4C_REPO_PORT="$(T4C_SERVER_PORT)" \
		-e T4C_REPO_NAME="$(T4C_IMPORTER_REPO)" \
		-e T4C_PROJECT_NAME="$(T4C_IMPORTER_PROJECT)" \
		-e T4C_USERNAME="$(T4C_USERNAME)" \
		-e T4C_PASSWORD="$(T4C_PASSWORD)" \
		-e LOG_LEVEL="$(LOG_LEVEL)" \
		$(DOCKER_PREFIX)$<:$$(echo "$(DOCKER_TAG_SCHEMA)" | envsubst) backup

run-t4c/client/exporter: t4c/client/base
	docker run $(DOCKER_RUN_FLAGS) \
		-e GIT_REPO_URL="$(GIT_REPO_URL)" \
		-e GIT_REPO_BRANCH="$(GIT_REPO_BRANCH)" \
		-e GIT_USERNAME="$(GIT_USERNAME)" \
		-e GIT_PASSWORD="$(GIT_PASSWORD)" \
		-e ENTRYPOINT="$(GIT_REPO_ENTRYPOINT)" \
		-e T4C_REPO_HOST="$(T4C_SERVER_HOST)" \
		-e T4C_REPO_PORT="$(T4C_SERVER_PORT)" \
		-e T4C_REPO_NAME="$(T4C_IMPORTER_REPO)" \
		-e T4C_PROJECT_NAME="$(T4C_IMPORTER_PROJECT)" \
		-e T4C_USERNAME="$(T4C_USERNAME)" \
		-e T4C_PASSWORD="$(T4C_PASSWORD)" \
		-e LOG_LEVEL="$(LOG_LEVEL)" \
		$(DOCKER_PREFIX)$<:$$(echo "$(DOCKER_TAG_SCHEMA)" | envsubst) export

debug-capella/base: DOCKER_RUN_FLAGS=-it --entrypoint="bash"
debug-capella/base: run-capella/base

debug-capella/remote: DOCKER_RUN_FLAGS=-it -p $(XPRA_DEBUG_PORT):10001
debug-capella/remote: run-capella/remote

debug-t4c/client/backup: LOG_LEVEL=DEBUG
debug-t4c/client/backup: DOCKER_RUN_FLAGS=-it --entrypoint="bash" -v $$(pwd)/backups/backup.py:/opt/capella/backup.py
debug-t4c/client/backup: run-t4c/client/backup

debug-t4c/client/remote/pure-variants: AUTOSTART_CAPELLA=0
debug-t4c/client/remote/pure-variants: DOCKER_RUN_FLAGS=-it --entrypoint="bash"
debug-t4c/client/remote/pure-variants: run-t4c/client/remote/pure-variants

t4c/server/server: SHELL=./capella_loop.sh
t4c/server/server:
	$(MAKE) -C t4c/server PUSH_IMAGES=$(PUSH_IMAGES) CAPELLA_VERSION=$$CAPELLA_VERSION $@

local-git-server: SHELL=./capella_loop.sh
local-git-server:
	docker build $(DOCKER_BUILD_FLAGS) -t $(DOCKER_PREFIX)$@:$$DOCKER_TAG tests/local-git-server
	$(MAKE) PUSH_IMAGES=$(PUSH_IMAGES) IMAGENAME=$@ .push

run-local-git-server: local-git-server
	docker run $(DOCKER_RUN_FLAGS) \
		-p $(GIT_SERVER_PORT):80 \
		$(DOCKER_PREFIX)$<:$$(echo "$(DOCKER_TAG_SCHEMA)" | envsubst)

ifeq ($(RUN_TESTS_WITH_T4C_SERVER), 1)
test: t4c/client/base local-git-server t4c/server/server
endif

ifeq ($(RUN_TESTS_WITH_T4C_CLIENT), 1)
test: t4c/client/remote
endif

test: SHELL=./capella_loop.sh
test:
	export CAPELLA_VERSION=$$CAPELLA_VERSION
	source .venv/bin/activate
	cd tests

	export PYTEST_MARKERS="not (t4c or t4c_server)"
	if [ "$(RUN_TESTS_WITH_T4C_SERVER)" == "1" ]
	then
		export PYTEST_MARKERS="$$PYTEST_MARKERS or t4c_server"
	fi

	if [ "$(RUN_TESTS_WITH_T4C_CLIENT)" == "1" ]
	then
		export PYTEST_MARKERS="$$PYTEST_MARKERS or t4c"
	fi

	pytest -o log_cli=true -s -m "$$PYTEST_MARKERS"

.push:
	@if [ "$(PUSH_IMAGES)" == "1" ]; \
	then \
		docker tag "$(DOCKER_PREFIX)$(IMAGENAME):$$DOCKER_TAG" "$(DOCKER_REGISTRY)/$(DOCKER_PREFIX)$(IMAGENAME):$$DOCKER_TAG"; \
		docker push "$(DOCKER_REGISTRY)/$(DOCKER_PREFIX)$(IMAGENAME):$$DOCKER_TAG";\
	fi

.PHONY: tests/* t4c/* t4c/server/* *
