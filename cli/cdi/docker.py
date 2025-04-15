# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import contextlib
import enum
import logging
import pathlib
import platform
import random
import shutil
import string
import subprocess
import typing as t

import typer
from rich import progress

from cdi import logging as logging_

log = logging.getLogger(__name__)


class SupportedArchitecture(str, enum.Enum):
    amd64 = "amd64"
    arm64 = "arm64"


def check_prerequisites() -> None:
    if not shutil.which("docker"):
        raise RuntimeError("Docker is required to run the CLI.")


def build_image_name(
    image_prefix: str, image_name: str, image_tag: str
) -> str:
    image_prefix = image_prefix.removesuffix("/")
    if image_prefix:
        return f"{image_prefix}/{image_name}:{image_tag}"
    return f"{image_name}:{image_tag}"


@contextlib.contextmanager
def build_dockerignore(
    context: str, dockerignore: list[str]
) -> t.Generator[None, None, None]:
    content = [
        "# Do not edit this file!",
        "# It's auto-generated during the build process and will be deleted after the build.",
        "",
        *dockerignore,
    ]
    dockerignore_file = pathlib.Path(context) / ".dockerignore"

    with dockerignore_file.open("w", encoding="utf-8") as f:
        for line in content:
            f.write(f"{line}\n")

    try:
        yield
    finally:
        dockerignore_file.unlink()


def build_image(
    *,
    image_name: str,
    build_context: str,
    build_architecture: SupportedArchitecture,
    no_cache: bool,
    build_args: dict[str, str] | None = None,
    labels: list[tuple[str, str]] | None = None,
) -> None:
    log.info("Start building Docker image '%s'...", image_name)

    cmd = ["build", build_context]
    if not build_args:
        build_args = {}
    for key, value in build_args.items():
        cmd.extend(["--build-arg", f"{key}={value}"])
    cmd.extend(["-t", image_name])
    cmd.extend(["--platform", f"linux/{build_architecture.value}"])
    if no_cache:
        cmd.append("--no-cache")
    if labels:
        for label_key, label_value in labels:
            cmd.extend(["--label", f"{label_key}={label_value}"])
    with progress.Progress(
        progress.SpinnerColumn(style="yellow"),
        progress.TextColumn("       [progress.description]{task.description}"),
        transient=True,
    ) as spinner:
        spinner.add_task(
            f"[yellow]Building Docker image '{image_name}'[/yellow]"
        )
        run_docker_subprocess(cmd)
    log.info("Successfully built Docker image '%s'", image_name)


def run_container(
    *,
    image_name: str,
    build_architecture: SupportedArchitecture,
    detach: bool,
    environment: dict[str, str] | None = None,
    volumes: dict[pathlib.Path, pathlib.PurePosixPath] | None = None,
    ports: dict[int, int] | None = None,
    debug: bool = False,
    args: list[str] | None = None,
    after_run_callback: t.Callable[[], None] | None = None,
) -> None:
    container_name = "cdi_" + "".join(
        random.choices(string.ascii_lowercase + string.digits, k=10)
    )
    log.info(
        "Running docker image '%s' as container '%s'...",
        image_name,
        container_name,
    )

    cmd = ["run"]

    if detach and debug:
        log.error("The options 'detach' and 'debug' are mutually exclusive.")
        raise typer.Exit(1)

    if detach:
        log.info(
            "Running in detached mode. To stop the container, run 'docker stop %s'.",
            container_name,
        )
        cmd.append("-d")

    if debug:
        cmd.append("-it")
        log.info(
            "Running in interactive debug mode. To exit the container, press 'CTRL' + 'D'. \n"
            "The keyboard is passed to the container. You can enter any commands."
        )
    else:
        log.info(
            "To stop the container, press 'CTRL' + 'C'. \n"
            "You can also start the container in detached mode by passing the '-d' option."
        )

    cmd.extend(["--name", container_name])

    if not environment:
        environment = {}
    for environment_key, environment_value in environment.items():
        cmd.extend(["-e", f"{environment_key}={environment_value}"])

    if not volumes:
        volumes = {}
    for host_volume, container_volume in volumes.items():
        cmd.extend(["-v", f"{host_volume.absolute()}:{container_volume}"])

    if not ports:
        ports = {}
    for host_port, container_port in ports.items():
        cmd.extend(["-p", f"{host_port}:{container_port}"])

    cmd.extend(["--platform", f"linux/{build_architecture.value}"])
    cmd.append("--add-host=host.docker.internal:host-gateway")
    cmd.append("--rm")

    if debug:
        cmd.extend(["--entrypoint", "bash"])

    cmd.append(image_name)

    if log.getEffectiveLevel() > logging_.DOCKER_LOG_LEVEL:
        log.info(
            "Container output is suppressed. To see the logs of the container, run 'docker logs %s -f'."
            " Alternatively, pass the '--verbose' flag to print the logs automatically.",
            container_name,
        )

    if not debug:
        cmd.extend(args or [])

    run_docker_subprocess(
        cmd, interactive=debug, after_command_callback=after_run_callback
    )


def push_image(
    image_name: str,
) -> None:
    log.info("Start pushing Docker image '%s'...", image_name)
    with progress.Progress(
        progress.SpinnerColumn(style="yellow"),
        progress.TextColumn("       [progress.description]{task.description}"),
        transient=True,
    ) as spinner:
        spinner.add_task(
            f"[yellow]Pushing Docker image '{image_name}'[/yellow]"
        )

        run_docker_subprocess(["push", image_name])
    log.info("Successfully pushed Docker image '%s'", image_name)


def run_docker_subprocess(
    cmd: list[str],
    *,
    interactive: bool = False,
    after_command_callback: t.Callable[[], None] | None = None,
) -> None:
    full_cmd = ["docker", *cmd]
    log.debug("Running Docker command: '%s'", " ".join(full_cmd))
    process = subprocess.Popen(
        full_cmd,
        stdout=None if interactive else subprocess.PIPE,
        stderr=None if interactive else subprocess.STDOUT,
    )
    if after_command_callback:
        after_command_callback()
    try:
        stdout = ""
        if process.stdout:
            for line in iter(process.stdout.readline, b""):
                decoded_line = line.decode("utf-8")
                stdout += decoded_line
                if interactive:
                    print(decoded_line, end="")
                else:
                    log.log(
                        logging_.DOCKER_LOG_LEVEL, decoded_line.strip("\n")
                    )
    except KeyboardInterrupt:
        process.terminate()
        print()
        raise typer.Abort() from None

    exit_code = process.wait()
    if exit_code != 0:
        if log.getEffectiveLevel() > logging_.DOCKER_LOG_LEVEL:
            log.info(stdout)
        log.error("Docker command failed with exit code %d", exit_code)
        raise typer.Exit(exit_code)


def get_current_cpu_architecture() -> SupportedArchitecture:
    architecture = platform.machine()
    if architecture == "x86_64":
        return SupportedArchitecture.amd64
    return SupportedArchitecture(platform.machine())
