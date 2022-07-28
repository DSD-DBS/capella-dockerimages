#!/bin/bash
echo -e "tmp_passwd\n$RMT_PASSWORD\n$RMT_PASSWORD" | passwd
unset RMT_PASSWORD

# Load git model
echo "---START_LOAD_MODEL---"

if [ $GIT_REVISION == "" ] && [ $GIT_DEPTH == 0]
then
    git clone $GIT_URL /home/techuser/model --no-checkout || r1=$?;
    git -C /home/techuser/model checkout $GIT_REVISION || r2=$?;
if [ $GIT_REVISION == "" ] && [ $GIT_DEPTH == 1]
then
    git clone $GIT_URL /home/techuser/model --no-single-branch --no-checkout --depth 1 || r1=$?;
    git -C /home/techuser/model checkout $GIT_REVISION || r2=$?;
if [ $GIT_REVISION != "" ] && [ $GIT_DEPTH == 0]
then
    git clone $GIT_URL /home/techuser/model --single-branch --branch $GIT_REVISION --no-checkout || r1=$?;
if [ $GIT_REVISION != "" ] && [ $GIT_DEPTH == 1]
then
    git clone $GIT_URL /home/techuser/model --single-branch --branch $GIT_REVISION --depth 1 --no-checkout || r1=$?;


if [ -n "$r1" -a "$r1" -ne 0 ] || [ -n "$r2" -a "$r2" -ne 0 ]
then
    echo "---FAILURE_LOAD_MODEL---"
    exit 1;
else
    echo "---FINISH_LOAD_MODEL---"
fi
unset GIT_USERNAME GIT_PASSWORD

# Prepare Workspace
echo "---START_PREPARE_WORKSPACE---"
export DISPLAY=:99;
Xvfb :99 -screen 0 1920x1080x8 -nolisten tcp &
/opt/capella/capella -data /workspace || r=$?;
if [[ -n "$r" ]] && [[ "$r" == 158 || "$r" == 0 ]]
then
    echo "---FINISH_PREPARE_WORKSPACE---"
else
    echo "---FAILURE_PREPARE_WORKSPACE---"
    exit 1;
fi


# Ensure that Capella is closed.
pkill java
pkill capella

rm /opt/scripts/*;

echo "---START_SESSION---"

exec supervisord
