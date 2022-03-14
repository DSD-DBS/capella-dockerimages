#!/bin/bash
set -e
if [ "$(whoami)" == "root" ];
then 
    echo -e "$RMT_PASSWORD\n$RMT_PASSWORD" | passwd techuser;
elif [ "$(whoami)" == "techuser" ];
then
    echo -e "tmp_passwd\n$RMT_PASSWORD\n$RMT_PASSWORD" | passwd;
else
    echo "Only techuser and root are supported as users.";
    exit 1;
fi

python3 /opt/setup_workspace.py;

# Replace environment variables in capella.ini, e.g. licences
envsubst < /opt/capella/capella.ini | tee /opt/capella/capella.ini;

exec supervisord
