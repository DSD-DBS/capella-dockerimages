<!--
 ~ SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

<!-- prettier-ignore -->
!!! info
    The Docker image name for this image is `capella/cli` / `t4c/client/cli`

The CLI images are meant to have a containerised Capella (with and without a
Team for Capella client) that can be run headless (as command line interface).

Both images build on top of the Capella base image or the T4C base image
respectively. They extend the base image with a virtual display and consider
an entrypoint that forwards all incoming command line flags to the capella
executable.

The image comes with a virtual display and integrates easily into CI/CD environments.

Capella provides some [CLI interfaces](https://github.com/eclipse/capella/blob/master/doc/plugins/org.polarsys.capella.commandline.doc/html/19.%20Command%20Line%20Support/19.1.%20Core%20Mechanism%20and%20Applications.mediawiki) out of the box, but the image can also be used to run custom eclipse plugins.

## Use the prebuilt image

```
docker run ghcr.io/dsd-dbs/capella-dockerimages/capella/ease:$TAG
```

where `$TAG` is the Docker tag. For more information, have a look at our [tagging schema](introduction.md#tagging-schema-for-prebuilt-images).

Please check the [`Run the container`](#run-the-container) section for more information about the usage.

## Build it yourself

### Build it manually with Docker

You can build a CLI image with the following command,
whereby you replace `$BASE` with `capella` or `t4c/client`.

```zsh
docker build -t $BASE/cli --build-arg BASE_IMAGE=$BASE/base cli
```

## Run the container

```zsh
docker run $BASE/cli -nosplash -consolelog -application APPLICATION -appid APPID [...]
```

with `$BASE` being one out of `capella` or `t4c/client`.

### Example to export representations (diagrams) as SVG images

Replace `/path/to/model` and `<PROJECT_NAME>` to pass any local Capella
model. Set the project name so that it fits your Capella project name for the
model as it is given in the file `/path/to/model/.project`.

Exported diagrams will appear on the host machine at
`/path/to/model/diagrams`.

```zsh
docker run --rm -it \
  -v /path/to/model:/model \
  capella/cli \
  -nosplash \
  -consolelog \
  -application org.polarsys.capella.core.commandline.core \
  -appid org.polarsys.capella.exportRepresentations \
  -data /workspace \
  -import /model \
  -input "/all" \
  -imageFormat SVG \
  -exportDecorations \
  -outputfolder /<PROJECT_NAME>/diagrams \
  -forceoutputfoldercreation
```
