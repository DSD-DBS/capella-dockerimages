#!/bin/bash
set -ex
echo -e "tmp_passwd\n$RMT_PASSWORD\n$RMT_PASSWORD" | passwd
unset RMT_PASSWORD

# Load git model
echo "---START_LOAD_MODEL---"

if [ "$GIT_REVISION" != "" ]
then
    FLAGS+=" --single-branch --branch $GIT_REVISION ";
fi

if [ -z $GIT_DEPTH ] && [ "$GIT_DEPTH" != "0" ]
then
    FLAGS+=" --depth $GIT_DEPTH ";
fi

git clone $GIT_URL /home/techuser/model $FLAGS;

if [ -n "$?" ] && [ "$?" -ne 0 ]
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
