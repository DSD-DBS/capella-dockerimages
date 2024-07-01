#!/bin/bash

# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

echo "Apply TeamForCapella client layer to Capella layer"
cp -R /layers/t4c/app/* /layers/capella/app
