#!/bin/bash
set -e

mkdir /tmp/model;
./capella \
    --launcher.suppressErrors \
    -nosplash -console -consoleLog \
    -data importer-workspace \
    -application com.thalesgroup.mde.melody.collab.importer \
    -checksize -1 -closeserveronfailure false \
    "$@" \
    -vmargs -Xms1000m -Xmx3000m -Xss4m -Dorg.eclipse.net4j.util.om.trace.disable=true \
    -hostname $T4C_REPO_HOST \
    -port $T4C_REPO_PORT \
    -reponame $T4C_REPO_NAME \
    -importerLogin "$T4C_USERNAME" \
    -importerPassword "$T4C_PASSWORD" \
    -outputFolder /tmp \
    -importCommitHistoryAsJson true;

mkdir /tmp/git;
git clone $GIT_REPO_URL /tmp/git; 
git switch $GIT_REPO_BRANCH || git switch -c $GIT_REPO_BRANCH;

/bin/cp -rf /tmp/$T4C_PROJECT_NAME/* /tmp/git;

cd /tmp/git;
git add .;
git diff --quiet && git diff --staged --quiet || git commit -m "Backup";
git push origin $GIT_REPO_BRANCH;