<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

<!-- prettier-ignore -->
!!! info
    The Docker image name for this image is `capella/ease` or `t4c/client/ease`

The EASE images build on top of Eclipse based images (the Capella base image or
the T4C base image) respectively. They extend the base image with support for
Python EASE scripts. These EASE scripts will run automatically during startup.

## Use the prebuilt image

```
docker run ghcr.io/dsd-dbs/capella-dockerimages/capella/ease:$TAG
```

where `$TAG` is the Docker tag. For more information, have a look at our
[tagging schema](./capella/introduction.md#tagging-schema-for-prebuilt-images).

Please check the [`Run the container`](#run-the-container) section to get an
overview over environment variables you have to set during startup.

## Build it yourself

### Preparation

#### Optional: Download Eclipse packages manually

If your network is restricted and doesn't have access to the public Eclipse
registries, you have to manually download and inject the packages. Luckily
capella is an application build within eclipse which offers a command line tool
for downloading resources from eclipse software repositories. Refer to
[this wiki article](https://wiki.eclipse.org/Equinox_p2_Repository_Mirroring#Running_the_Mirroring_Tools)
if you are interested to learn the capabilities of the eclipse mirroring tool.

You have to run the following commands for each of these following urls to
download the metadata and artifact for the packages:

- <https://eclipse.py4j.org/>
- <https://download.eclipse.org/ease/integration/nightly/>
- <https://download.eclipse.org/technology/swtbot/releases/latest/>

```zsh
capella -nosplash -verbose
-application org.eclipse.equinox.p2.artifact.repository.mirrorApplication
-source <url>
-destination <destionation_path> (e.g. file:ease/extensions/<extension>)>
```

```zsh
capella -nosplash -verbose
-application org.eclipse.equinox.p2.metadata.repository.mirrorApplication
-source <url>
-destination <destionation_path> (e.g. file:ease/extensions/<extension>)>
```

where `<extension>` is `py4j`, `ease` or `swtbot`. `capellac` is the path to
the capella executable laying in the capella directory
(capella.zip/capella/capella). If you have build an AppImage (linux) or a
shortcut for it you can also call this with the displayed options.

Each directory `ease/extensions/<extension>` should have the following
structure:

- `content.jar`
- `artifacts.jar`
- `plugins/`
  - `*.jar` files
- `features/`
  - `*.jar` files

### Build it manually with Docker

If your network is unrestricted, you can build an EASE image with the following
command, whereby you replace `$BASE` with `capella` or `t4c/client`.

```zsh
docker build -t $BASE/ease \
    --build-arg BASE_IMAGE=$BASE/base \
    --build-arg BUILD_TYPE=online \
    ease
```

If your network is restricted, please execute the steps described in
[Download Eclipse Packages manually](#optional-download-eclipse-packages-manually).
When your extensions are located in `ease/extensions` and the right subfolders,
please run:

```zsh
docker build -t $BASE/ease \
    --build-arg BASE_IMAGE=$BASE/base \
    --build-arg BUILD_TYPE=offline \
    ease
```

## Run the container

Run the container with this command and provide EASE Python scripts as a
volume. The scripts have to be located in the `/opt/scripts` directory (inside
the container)!

For more information refer to:
[How does a EASE Python Script look like?](#how-does-an-ease-python-script-look-like).

To run the container, just execute:

```zsh
docker run -v script.py:/opt/scripts/script.py $BASE/ease
```

where `$BASE` is again `capella` or `t4c/client`.

### Miscellaneous

#### How does an EASE Python script look like?

In general, you can try to execute the Py4J in the Eclipse environment for
development purposes first. When the script is tested, you can use it in our
container.

Please make sure that any EASE Python scripts have the `onStartup` comment in
the header. That can be the first line or the first line after the module
docstring. This is required, otherwise the scripts will not be auto-executed.

```python
# onStartup: 0
```

An example script using our PyEclipseEase library could look like:

```python
# onStartup: 0
import pyease.ease

if __name__ == "__main__":
    logger = ease.logger
    ease.log_to_file(os.environ["EASE_LOG_LOCATION"])

    pyease.ease.open_eclipse_perspective("Capella")
    logger.info("Hello world!")

    pyease.ease.kill_capella_process(30)
```
