# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

builder:
	docker build builder -t k3d-myregistry.localhost:12345/buildpacks-base -t buildpacks-base
	docker push k3d-myregistry.localhost:12345/buildpacks-base
	pack builder create localhost:12345/mbse-builder \
		--config builder/builder.toml
	docker push localhost:12345/mbse-builder

capella: builder
	pack build capella-test \
		--env CAPELLA_VERSION=6.0.0 \
		--builder localhost:12345/mbse-builder \
		--path /Users/moritzweber/Projects/github/capella-collab-manager/capella-dockerimages/buildpacks \
		--pull-policy always \
		--volume $$PWD/..:/app:ro \
		--network host

# pack build capella-test \
# 	--env CAPELLA_VERSION=6.0.0 \
# 	--builder mbse-builder \
# 	--volume $$PWD/..:/app:ro \
# 	--network host \
# 	--verbose

.PHONY: *
