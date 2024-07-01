<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Memory options for Eclipse

!!! info

    This section applies if using `eclipse`, `capella` or `papyrus`.

To specify fixed memory options for the JVM, you can pass the following
environment variables to the `docker run` commands:

- `MEMORY_MIN` (default `70%`), translated to `-Xms` for absolute values and
  `-XX:InitialRAMPercentage` and `-XX:MinRAMPercentage` for percentage values.
  Percentage values are calculated according to the total memory or the
  requested memory by the container.
- `MEMORY_MAX` (default `90%`), translated to `-Xmx` for absolute values and
  `-XX:MaxRAMPercentage` for percentage values. Percentage values are
  calculated according to the total memory of the system or the total memory
  available to the container.

If the value ends with a %, we assume that it's a percentage value.

- If used in a Kubernetes cluster, it determines the values from the Pod
  requests/limits.
- If used on a host system, it determines the value from the host memory.

See also:

- https://stackoverflow.com/a/65327769
- https://www.merikan.com/2019/04/jvm-in-a-container/#java-10
