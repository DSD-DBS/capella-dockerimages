# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

# Add prefix to all dockerimage names, e.g. capella-collab
DOCKER_PREFIX ?=

# T4C license secret (usually a long numeric string)
T4C_LICENCE_SECRET ?= XXX

# Predefined T4C repositories (comma separated), e.g. testrepo,testrepo2
T4C_REPOSITORIES ?= testrepo

# T4C server host
T4C_SERVER_HOST ?= localhost

# T4C server port
T4C_SERVER_PORT ?= 2036

# Predefined T4C username (for the connection dialog or for the importer)
T4C_USERNAME ?= admin

# T4C password for the importer
T4C_PASSWORD ?= admin

# Remote container rdp password
RMT_PASSWORD ?= tmp_passwd2

# Git repository url for the importer, e.g. https://github.com/example.git
GIT_REPO_URL ?= https://github.com/example.git

# Git repository branch for the importer, e.g. main
GIT_REPO_BRANCH ?= main

# T4C repository name for the importer, e.g. repoCapella
T4C_IMPORTER_REPO ?= repo-name

# T4C project name for the importer, e.g. project
T4C_IMPORTER_PROJECT ?= project-name

# Git username for the importer to push changes
GIT_USERNAME ?= username

# Git password for the importer to push changes
GIT_PASSWORD ?= password

# Preferred RDP port on your host system
RDP_PORT ?= 3390

# Preferred fileservice port on your host system
FILESYSTEM_PORT ?= 8081

# Preferred metrics port on your host system
METRICS_PORT ?= 9118

# Preferred Capella version
CAPELLA_VERSION ?= 5.2.0

DOCKER_TAG ?= latest

all: \
	base \
	capella/base \
	capella/cli \
	capella/remote \
	t4c/client/base \
	t4c/client/cli \
	t4c/client/remote \
	capella/ease \
	capella/ease/remote \
	t4c/client/ease \
	capella/readonly \
	t4c/client/importer

base:
	docker build -t $(DOCKER_PREFIX)$@ base

capella/base:
	docker build -t $(DOCKER_PREFIX)$@:$(DOCKER_TAG) --build-arg BUILD_TYPE=online --build-arg CAPELLA_VERSION=$(CAPELLA_VERSION) capella

capella/cli:
	docker build -t $(DOCKER_PREFIX)$@:$(DOCKER_TAG) --build-arg BASE_IMAGE=$(DOCKER_PREFIX)capella/base:$(DOCKER_TAG) cli

capella/remote:
	docker build -t $(DOCKER_PREFIX)$@:$(DOCKER_TAG) --build-arg BASE_IMAGE=$(DOCKER_PREFIX)capella/base:$(DOCKER_TAG) remote

t4c/client/base:
	docker build -t $(DOCKER_PREFIX)$@:$(DOCKER_TAG) --build-arg BASE_IMAGE=$(DOCKER_PREFIX)capella/base:$(DOCKER_TAG) t4c

t4c/client/cli:
	docker build -t $(DOCKER_PREFIX)$@:$(DOCKER_TAG) --build-arg BASE_IMAGE=$(DOCKER_PREFIX)t4c/client/base:$(DOCKER_TAG) cli

t4c/client/remote:
	docker build -t $(DOCKER_PREFIX)$@:$(DOCKER_TAG) --build-arg BASE_IMAGE=$(DOCKER_PREFIX)t4c/client/base:$(DOCKER_TAG) remote

capella/ease:
	docker build -t $(DOCKER_PREFIX)$@:$(DOCKER_TAG) --build-arg BASE_IMAGE=$(DOCKER_PREFIX)capella/base:$(DOCKER_TAG) --build-arg BUILD_TYPE=online ease

capella/ease/remote:
	docker build -t $(DOCKER_PREFIX)$@:$(DOCKER_TAG) --build-arg BASE_IMAGE=$(DOCKER_PREFIX)capella/ease:$(DOCKER_TAG) remote

t4c/client/ease:
	docker build -t $(DOCKER_PREFIX)$@:$(DOCKER_TAG) --build-arg BASE_IMAGE=$(DOCKER_PREFIX)t4c/client/base:$(DOCKER_TAG) --build-arg BUILD_TYPE=online ease

capella/readonly:
	docker build -t $(DOCKER_PREFIX)$@:$(DOCKER_TAG) --build-arg BASE_IMAGE=$(DOCKER_PREFIX)capella/ease/remote:$(DOCKER_TAG) readonly

t4c/client/importer:
	docker build -t $(DOCKER_PREFIX)$@:$(DOCKER_TAG) --build-arg BASE_IMAGE=$(DOCKER_PREFIX)t4c/client/base:$(DOCKER_TAG) importer

run/t4c/client/remote:
	docker rm /t4c-client-remote || true
	docker run -d \
		-e T4C_LICENCE_SECRET=$(T4C_LICENCE_SECRET) \
		-e T4C_SERVER_HOST=$(T4C_SERVER_HOST) \
		-e T4C_SERVER_PORT=$(T4C_SERVER_PORT) \
		-e T4C_REPOSITORIES=$(T4C_REPOSITORIES) \
		-e RMT_PASSWORD=$(RMT_PASSWORD) \
		-e FILESERVICE_PASSWORD=$(RMT_PASSWORD) \
		-e T4C_USERNAME=$(T4C_USERNAME) \
		-p $(RDP_PORT):3389 \
		-p $(FILESYSTEM_PORT):8000 \
		-p $(METRICS_PORT):9118 \
		--name t4c-client-remote \
		$(DOCKER_PREFIX)t4c/client/remote

run/t4c/client/importer:
	docker run \
		--network="host" \
		-it \
		--entrypoint="/bin/bash" \
		-e EASE_LOG_LOCATION=/proc/1/fd/1 \
		-e GIT_REPO_URL=$(GIT_REPO_URL) \
		-e GIT_REPO_BRANCH=$(GIT_REPO_BRANCH) \
		-e T4C_REPO_HOST=$(T4C_SERVER_HOST) \
		-e T4C_REPO_PORT=$(T4C_SERVER_PORT) \
		-e T4C_REPO_NAME=$(T4C_IMPORTER_REPO) \
		-e T4C_PROJECT_NAME=$(T4C_IMPORTER_PROJECT) \
		-e T4C_USERNAME=$(T4C_USERNAME) \
		-e T4C_PASSWORD=$(T4C_PASSWORD) \
		-e GIT_USERNAME=$(GIT_USERNAME) \
		-e GIT_PASSWORD=$(GIT_PASSWORD) \
		$(DOCKER_PREFIX)t4c/client/importer

.PHONY: *
