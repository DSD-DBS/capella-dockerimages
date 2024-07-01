#!/bin/bash

# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

# Replace environment variables in capella.ini, e.g. licences
envsubst < /layers/capella/capella/capella.ini > /tmp/capella.ini && mv /tmp/capella.ini /layers/capella/capella/capella.ini;
