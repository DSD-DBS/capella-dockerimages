# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import filecmp
import logging
import pathlib
import platform
import typing as t

from rich import pretty

from . import _repository_root, docker

log = logging.getLogger()


def get_current_cpu_architecture() -> docker.SupportedArchitecture:
    architecture = platform.machine()
    if architecture == "x86_64":
        return docker.SupportedArchitecture.amd64
    return docker.SupportedArchitecture(platform.machine())


def print_cli_options(options: dict[str, t.Any]):
    log.debug(
        "Using the following CLI options: \n%s", pretty.pretty_repr(options)
    )


def copy_memory_flags_file(memory_flags_target: pathlib.Path):
    memory_flags_source = _repository_root / "eclipse" / "set_memory_flags.py"

    if not memory_flags_target.exists() or not filecmp.cmp(
        memory_flags_source, memory_flags_target
    ):
        log.warning(
            "%s is out of date. Overwriting file with eclipse/set_memory_flags.py",
            memory_flags_target.relative_to(_repository_root),
        )
        memory_flags_target.write_text(memory_flags_source.read_text())
