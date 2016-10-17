#!/usr/bin/env bash

############
# Download this file and execute it to download and install everything else in this repo
# ----------

GITHUBNAME="ansible-ubuntu-bootstrap"
GITHUBID="614b61e8f756f0b5b4de42a0dba164e811ddd7f4"

INSTALLIT="???"
while [ "${INSTALLIT}" != "y" -a "${INSTALLIT}" != "n" ]; do
    echo -n "Do you want to start the installation after download? [y/n]: "; read -n1 INSTALLIT
    echo    ""
done

wget "https://github.com/masu33/${GITHUBNAME}/archive/${GITHUBID}.zip"
unzip "${GITHUBID}.zip"

if [ "${INSTALLIT}" == "n" ]; then
    exit 0
else
    cd "${GITHUBNAME}-${GITHUBID}"
    ./tools/prerequisites.sh
    ./tools/ansible_start.sh
    cd -
fi
