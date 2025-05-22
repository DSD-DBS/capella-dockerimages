# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import filecmp
import logging
import pathlib
import subprocess
import typing as t

import typer
from rich import pretty

from . import _repository_root, args

log = logging.getLogger(__name__)


def print_cli_options(options: dict[str, t.Any], context: str) -> None:
    log.debug(
        "Using the following CLI options for %s: \n%s",
        context,
        pretty.pretty_repr(options),
    )


def copy_memory_flags_file(memory_flags_target: pathlib.Path) -> None:
    memory_flags_source = _repository_root / "eclipse" / "set_memory_flags.py"

    if not memory_flags_target.exists() or not filecmp.cmp(
        memory_flags_source, memory_flags_target
    ):
        log.warning(
            "%s is out of date. Overwriting file with eclipse/set_memory_flags.py",
            memory_flags_target.relative_to(_repository_root),
        )
        memory_flags_target.write_text(memory_flags_source.read_text())


def whitelist_xhost() -> None:
    log.info(
        "Changing X11 configuration to allow network connections from localhost..."
    )
    subprocess.run(["xhost", "+localhost"], check=True)


def configure_x_server_connection(
    environment: dict[str, str],
    *,
    connect_to_x_server: bool,
) -> None:
    if connect_to_x_server:
        whitelist_xhost()
        environment["DISPLAY"] = "host.docker.internal:0"
        environment["USE_VIRTUAL_DISPLAY"] = "0"


def configure_remote_connection(
    environment: dict[str, str],
    ports: dict[int, int],
    *,
    connection_method: args.ConnectionMethod,
    xpra_subpath: str,
    rdp_password: str | None,
    rdp_port: int,
    xpra_port: int,
) -> None:
    environment["CONNECTION_METHOD"] = connection_method.value
    environment["XPRA_SUBPATH"] = xpra_subpath
    environment["RMT_PASSWORD"] = rdp_password if rdp_password else ""

    if connection_method == args.ConnectionMethod.XRDP:
        ports[rdp_port] = 3389

    if connection_method == args.ConnectionMethod.XPRA:
        ports[xpra_port] = 10000


def remote_callback_factory(
    *,
    remote: bool,
    connection_method: args.ConnectionMethod,
    rdp_port: int,
    xpra_port: int,
    xpra_subpath: str,
) -> t.Callable[[], None]:
    def remote_callback() -> None:
        if remote:
            if connection_method == args.ConnectionMethod.XRDP:
                log.info(
                    "To connect to the container, start any RDP client and connect to localhost:%s",
                    rdp_port,
                )
            if connection_method == args.ConnectionMethod.XPRA:
                log.info(
                    "To connect to the container, connect to http://localhost:%s%s/ in a browser or run 'xpra attach ws://localhost:%s%s/'",
                    xpra_port,
                    xpra_subpath,
                    xpra_port,
                    xpra_subpath,
                )

    return remote_callback


def transform_labels(labels: list[str] | None) -> list[tuple[str, str]]:
    """Resolve the key=value structure of the labels and return a list of tuples."""
    if not labels:
        return []

    transformed_labels = []
    for label in labels:
        split_label = label.split("=")
        if len(split_label) != 2:  # noqa: PLR2004
            log.error("Label '%s' is not in the format 'key=value'.", label)
            raise typer.Exit(1)
        transformed_labels.append((split_label[0], split_label[1]))

    return transformed_labels
