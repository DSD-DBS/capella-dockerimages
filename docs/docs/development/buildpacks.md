<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Build Images with Cloud Native Buildpacks

Starting with version 3.0.0, we use Cloud Native Buildpacks for the Capella
based images.

## Why Cloud Native Buildpacks?

### Disadvantages of Dockerfiles

Before v3.0.0, we have used Dockerfiles to build the images. To keep the system
dependencies up to date, we have regularly rebuilt the images without build
cache.

In combination with bad use of multi-stage builds, this has led to enormous
image sizes and long build times. Image layers were not cached at all. Our
internal Docker registry has grown to several terabytes in size.

In addition, pulling the images from the registry was slow and after updates,
all layers had to be pulled again.

### Advantages of Buildpacks for our Images

- Exchange individual layers. Some examples where this is useful:
  - Update the dependencies without update of the Capella layer
  - Update TeamForCapella archive without update of the Capella layer
  - Update dropins independently
- Reduction of the image sizes = faster image pull times = faster session
  startup in the Collaboration Manager. Examples:
  - `capella/base:6.0.0`: 3.5GB -> 1.5GB
  - `t4c/client/base:6.0.0`: 4.5GB -> 1.6GB
- Reuse layers of last builds, massively reducing storage space and traffic in
  registries Less layers, the new layers are clearly mentioned and separated in
  different scopes (capella layer, capella-dropins layer, t4c-client layer,
  ...)
- Full reproducible builds (same input = same digest of output images)
- No extensive build cache which sums up in local development (instead, it uses
  layers of the last image as cache)
- It makes the images modular. Users can decide which modules they want to have
  in their images (e.g. add xpra or xrdp as add-on to get remote support)
- Reduce number of layers in the images.

### Two layers: Meta and App

To have consistent naming, we've decided that we want to allow each buildpack
to define two layers:

- `meta` layer: contains `exec.d` scripts, entrypoint scripts, and other
  customizations which change frequently.
- `app` layer: contains the application (e. g. Capella, Eclipse, ...) and other
  files which change less frequently. As the app layer is larger in size, we
  want to cache it as much as possible.

## Get Started with Buildpacks

If you want to learn more about buildbacks, check their documentation:
https://buildpacks.io/docs/
