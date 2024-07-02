#!/bin/bash
# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

python3 /layers/capella/startup/set_memory_flags.py
xvfb-run /layers/capella/capella/capella "$@"
