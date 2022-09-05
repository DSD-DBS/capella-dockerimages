#!/bin/bash
# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

set -ex

mkdir /tmp/model;
./importer.sh \
    -hostname $T4C_REPO_HOST \
    -port ${T4C_REPO_PORT:-2036} \
    -reponame $T4C_REPO_NAME \
    -projectName $T4C_PROJECT_NAME \
    -importerLogin "$T4C_USERNAME" \
    -importerPassword "$T4C_PASSWORD" \
    -outputFolder /tmp/model \
    -archiveProject false \
    -importCommitHistoryAsJson true \
    -includeCommitHistoryChanges true \
    -consoleport ${T4C_CDO_PORT:-12036};

mkdir /tmp/git;
git clone $GIT_REPO_URL /tmp/git;
cd /tmp/git;
git switch $GIT_REPO_BRANCH || git switch -c $GIT_REPO_BRANCH;

/bin/cp -rf /tmp/model/*/* /tmp/git;
/bin/cp -f /tmp/model/CommitHistory__*.json /tmp/git/CommitHistory.json;
/bin/cp -f /tmp/model/CommitHistory__*.activitymetadata /tmp/git/CommitHistory.activitymetadata;

git config user.email ${GIT_EMAIL:-backup@example.com}
git config user.name $GIT_USERNAME

git add .;
git diff --quiet && git diff --staged --quiet || git commit --message "Backup";

git push origin $GIT_REPO_BRANCH;
