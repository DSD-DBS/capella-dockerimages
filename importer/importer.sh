# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

./capella \
    --launcher.suppressErrors \
    -nosplash -console -consoleLog \
    -data importer-workspace \
    -application com.thalesgroup.mde.melody.collab.importer \
    -checksize -1 -closeserveronfailure false \
    "$@" \
    -vmargs -Xms1000m -Xmx3000m -Xss4m -Dorg.eclipse.net4j.util.om.trace.disable=true \
