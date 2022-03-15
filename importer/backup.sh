#!/bin/bash
set -ex

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

export T4C_PROJECT_NAME_CLEANED=$(echo "$T4C_PROJECT_NAME" | sed -e "s/%20/ /g")

/bin/cp -rf "/tmp/model/$T4C_PROJECT_NAME_CLEANED/"* /tmp/git;

git config user.email backup@capella.ertms.be
git config user.name Backup

git add .;
git diff --quiet && git diff --staged --quiet || git commit --message "Backup";

cat << EOF > ~/.netrc
machine github.com
    login $GIT_USERNAME
    password $GIT_PASSWORD
EOF

git push origin $GIT_REPO_BRANCH;
