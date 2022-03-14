#!/bin/bash
set -e

mkdir /tmp/model;
./importer.sh \
    -hostname $T4C_REPO_HOST \
    -port $T4C_REPO_PORT \
    -reponame $T4C_REPO_NAME \
    -projectName $T4C_PROJECT_NAME \
    -importerLogin "$T4C_USERNAME" \
    -importerPassword "$T4C_PASSWORD" \
    -outputFolder /tmp/model \
    -archiveProject false \
    -importCommitHistoryAsJson true;

mkdir /tmp/git;
git clone $GIT_REPO_URL /tmp/git;
cd /tmp/git;
git switch $GIT_REPO_BRANCH || git switch -c $GIT_REPO_BRANCH;

/bin/cp -rf /tmp/model/$T4C_PROJECT_NAME/* /tmp/git;

git add .;
git diff --quiet && git diff --staged --quiet || git commit -m "Backup";
git push origin $GIT_REPO_BRANCH;