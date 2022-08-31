#!/bin/bash
# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

set -e

Xvfb :99 -screen 0 1920x1080x8 -nolisten tcp & ./backup.sh
