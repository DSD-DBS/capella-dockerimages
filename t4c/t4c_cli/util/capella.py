# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import logging
import os
import pathlib
import re
import subprocess
import sys
import textwrap
import typing as t

from . import config

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
log = logging.getLogger(__name__)

DEFAULT_CAPELLA_COMMAND = [
    "/opt/capella/capella",
    "--launcher.suppressErrors",
    "-nosplash",
    "-console",
    "-consoleLog",
    "-data",
    "workspace",
]


def run_capella_command_and_handle_errors(
    application: str,
    arguments: list[str],
    stdout_line_validator: t.Callable[[str], None] | None = None,
) -> tuple[str, str]:
    """Run the provided Capella command.

    The function validates the stdout of the command using the provided validator.
    The validator is executed on each of stdout. An example validator looks like:

    ```py
    def validate_line(line: str):
        if "failure" in line:
            raise RuntimeError()
    ```
    """

    command = [
        *DEFAULT_CAPELLA_COMMAND,
        "-application",
        application,
        *arguments,
    ]
    log.info("Executing the following command: %s", " ".join(command))

    stderr = ""
    stdout = ""
    with subprocess.Popen(
        command,
        cwd="/opt/capella",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    ) as popen:
        assert popen.stdout
        for line in popen.stdout:
            stdout += line

            print(
                textwrap.indent(
                    line,
                    "[STDOUT] ",
                ),
                end="",
                flush=True,
            )

            if (
                "Team for Capella server unreachable" in line
                or "Name or service not known" in line
            ):
                raise RuntimeError("Team for Capella server unreachable")

            if "Repository not found" in line:
                log.error(
                    'Repository "%s" does not exist',
                    config.config.t4c.repo_name,
                )
                sys.exit(1)

            if stdout_line_validator:
                stdout_line_validator(line)

        if popen.stderr:
            stderr = popen.stderr.read()
            print("[STDERR] " + stderr, end="")

    if (return_code := popen.returncode) != 0:
        raise RuntimeError(
            f"Capella command failed with exit code {return_code}"
        )

    return stdout, stderr


def is_capella_7_x_x() -> bool:
    return bool(re.match(r"7.[0-9]+.[0-9]+", config.config.capella.version))


def is_capella_5_x_x() -> bool:
    return bool(re.match(r"5.[0-9]+.[0-9]+", config.config.capella.version))


def is_capella_5_0_x() -> bool:
    return bool(re.match(r"5.0.[0-9]+", config.config.capella.version))


def determine_model_dir(
    root_path: pathlib.Path,
    entrypoint: str | None,
    create_if_not_exist: bool = False,
) -> pathlib.Path:
    model_dir = root_path
    if entrypoint:
        model_dir = pathlib.Path(
            root_path, str(pathlib.Path(entrypoint)).lstrip("/")
        )

    if not create_if_not_exist and not model_dir.exists():
        raise FileNotFoundError(model_dir)

    if model_dir.is_file():
        log.warning(
            "The entrypoint '%s' is a file."
            " Due to limitations with the TeamForCapella CLI, "
            " we're falling back to the parent directory as model directory.",
            entrypoint,
        )
        model_dir = model_dir.parent

    if create_if_not_exist:
        model_dir.mkdir(exist_ok=True, parents=True)

    return model_dir
