# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import logging
import textwrap

log = logging.getLogger(__name__)


def log_subprocess_error(
    return_code: int, cmd: list[str], stdout: str, stderr: str
) -> None:
    """Log the error of a subprocess in a readable format.

    Do not pass credentials to the `cmd` parameter.
    """

    logging.error(
        "Command failed with return code %d. See stacktrace below.\n%s\n%s\n%s",
        return_code,
        textwrap.indent(
            " ".join(cmd),
            "[COMMAND] ",
        ),
        textwrap.indent(
            stdout,
            "[STDOUT] ",
        ),
        textwrap.indent(
            stderr,
            "[STDERR] ",
        ),
    )
