# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0
"""Set the memory flags in the *.ini file for Eclipse applications.

The script reads the following environment variable:

ECLIPSE_EXECUTABLE: The path to the eclipse executable.
MEMORY_MIN: The minimum memory that the JVM should use.
            Check the set_memory_flags function for more information.
MEMORY_MAX: The maximum memory that the JVM should use.
            Check the set_memory_flags function for more information.

The script is called during container startup.
"""

import os
import pathlib


def remove_all_memory_flags(file_content: list[str]) -> list[str]:
    """Remove all memory flags from *.ini files.

    To make sure that we don't have any conflicting memory flags in the
    .ini file, we remove all flags that start with -Xm.

    This will explicitely remove the -Xms and -Xmx flags.
    """

    return [line for line in file_content if not line.lstrip().startswith("-Xm")]


def set_memory_flags(file_content: list[str], memory_min: str, memory_max: str) -> None:
    """Set the memory flags in *.ini.

    If the value of memory_max ends with a %, we assume that it's a percentage value.
    - If used in a Kubernetes cluster, it determines the values from the Pod requests/limits.
    - If used on a host system, it determines the value from the host memory.

    See Also
    --------
    - https://stackoverflow.com/a/65327769
    - https://www.merikan.com/2019/04/jvm-in-a-container/#java-10
    """

    if memory_min.strip().endswith("%"):
        append_flag_to_file(
            file_content, "XX:InitialRAMPercentage=", memory_min.strip("%")
        )
        append_flag_to_file(file_content, "XX:MinRAMPercentage=", memory_min.strip("%"))
    else:
        append_flag_to_file(file_content, "Xms", memory_min)

    if memory_max.strip().endswith("%"):
        append_flag_to_file(file_content, "XX:MaxRAMPercentage=", memory_max.strip("%"))
    else:
        append_flag_to_file(file_content, "Xmx", memory_max)


def print_vm_memory_usage_during_start(file_content: list[str]) -> None:
    """Print the JVM memory options during start."""

    file_content.append("-XshowSettings:vm")


def append_flag_to_file(file_content: list[str], flag: str, value: str) -> None:
    """Append a flag to the *.ini file."""

    file_content.append(f"-{flag}{value}")


if __name__ == "__main__":
    eclipse_executable = pathlib.Path(os.environ["ECLIPSE_EXECUTABLE"])
    _memory_min = os.environ["MEMORY_MIN"].strip()
    _memory_max = os.environ["MEMORY_MAX"].strip()

    ini_path = eclipse_executable.with_suffix(".ini")

    _file_content = ini_path.read_text("utf-8").splitlines()

    _file_content = remove_all_memory_flags(_file_content)
    set_memory_flags(_file_content, _memory_min, _memory_max)
    print_vm_memory_usage_during_start(_file_content)

    ini_path.write_text("\n".join(_file_content), encoding="utf-8")
