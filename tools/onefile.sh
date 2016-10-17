#!/usr/bin/env bash

############
# Download this file and execute it to download and install everything else in this repo
# ----------

GITHUBNAME="ansible-ubuntu-bootstrap"

INSTALLIT="???"
while [ "${INSTALLIT}" != "y" -a "${INSTALLIT}" != "n" ]; do
    echo -n "Do you want to start the installation after download? [y/n]: "; read -n1 INSTALLIT
    echo    ""
done

sudo apt-get install git <<< "y"

git clone "https://github.com/masu33/${GITHUBNAME}.git"

if [ "${INSTALLIT}" == "n" ]; then
    exit 0
else
    cd "${GITHUBNAME}"
    ./tools/prerequisites.sh
    ./tools/ansible_start.sh
    cd -
fi
