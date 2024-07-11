#!/bin/bash

# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

cat >> /layers/capella/app/capella.ini <<EOT
-DOBEO_LICENSE_SERVER_CONFIGURATION=$T4C_LICENCE_SECRET
-Duser.name=$T4C_USERNAME
-Dfr.obeo.dsl.viewpoint.collab.import.gmf.notation.keep.cdoid.as.xmiid=true
-Dfr.obeo.dsl.viewpoint.collab.import.other.elements.keep.cdoid.as.xmiid=true
EOT
