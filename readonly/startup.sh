#!/bin/bash
echo -e "tmp_passwd\n$RMT_PASSWORD\n$RMT_PASSWORD" | passwd

# Load git model
echo "---START_LOAD_MODEL---"
if ! git clone "$GIT_URL" /home/techuser/model -b "$GIT_REVISION"
then 
    echo "---FAILURE_LOAD_MODEL---"
    exit 1;
else 
    echo "---FINISH_LOAD_MODEL---"
fi

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

unset GIT_USERNAME;
unset GIT_PASSWORD;
rm /opt/scripts/*;

echo "---START_SESSION---"

exec supervisord
