# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0
export CAPELLA_VERSION ?= 7.0.0

base:
	uv run cdi build base

jupyter-notebook: base
	uv run cdi build jupyter \
		--skip-base-image

capella/base: base
	uv run cdi build capella \
		--no-remote \
		--skip-base-image

papyrus/base:
	uv run cdi build papyrus \
		--no-remote

eclipse/base: base
	uv run cdi build eclipse \
		--skip-base-image \
		--no-remote

capella/remote: capella/base
	uv run cdi build capella \
		--skip-base-image \
		--skip-capella-image

papyrus/remote: papyrus/base
	uv run cdi build papyrus \
		--skip-papyrus-image \
		--skip-base-image

eclipse/remote: eclipse/base
	uv run cdi build eclipse \
		--skip-base-image \
		--skip-eclipse-image

eclipse/remote/pure-variants: base
	uv run cdi build eclipse \
		--skip-base-image \
		--remote \
		--pv-client \
		--image-tag '{eclipse_version}-{pure_variants_version}-{cdi_revision}'

t4c/client/base: capella/base
	uv run cdi build capella \
		--t4c-client \
		--no-remote \
		--skip-base-image \
		--skip-capella-image

t4c/client/remote: capella/base
	uv run cdi build capella \
		--t4c-client \
		--remote \
		--skip-base-image \
		--skip-capella-image

t4c/client/remote/pure-variants: base
	uv run cdi build capella \
		--t4c-client \
		--remote \
		--pv-client \
		--skip-base-image \
		--image-tag '{capella_version}-{pure_variants_version}-{cdi_revision}'

capella/remote/pure-variants: base
	uv run cdi build capella \
		--remote \
		--pv-client \
		--skip-base-image \
		--image-tag '{capella_version}-{pure_variants_version}-{cdi_revision}'

run-capella/base: capella/base
	uv run cdi run capella \
		--skip-build \
		--no-remote

run-jupyter-notebook: jupyter-notebook
	uv run cdi run jupyter \
		--skip-build

run-capella/remote: capella/remote
	uv run cdi run capella \
		--skip-build

run-papyrus/remote: papyrus/remote
	uv run cdi run papyrus \
		--skip-build

run-eclipse/remote: eclipse/remote
	uv run cdi run eclipse \
		--skip-build

run-eclipse/remote/pure-variants: eclipse/remote/pure-variants
	uv run cdi run eclipse \
       	--pv-client \
		--skip-build \
		--image-tag '{eclipse_version}-{pure_variants_version}-{cdi_revision}'

run-t4c/client/remote: t4c/client/remote
	uv run cdi run capella \
		--t4c-client \
		--remote

run-t4c/client/remote/pure-variants: t4c/client/remote/pure-variants
	uv run cdi run capella \
		--t4c-client \
		--pv-client \
		--remote \
		--image-tag '{capella_version}-{pure_variants_version}-{cdi_revision}'

local-git-server:
	docker build -t $@ local-git-server

run-local-git-server: local-git-server
	docker run --rm -it \
		-p 10001:80 \
		$<

capella/builder:
	docker build -t $@ builder
	docker run -it -e CAPELLA_VERSION=$(CAPELLA_VERSION) -v $$(pwd)/builder/output/$(CAPELLA_VERSION):/output -v $$(pwd)/builder/m2_cache:/root/.m2/repository $@

.PHONY: t4c/* *
