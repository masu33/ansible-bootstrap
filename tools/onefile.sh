#!/usr/bin/env bash

############
# Download this file and execute it to download and install everything else in this repo
# ----------

GITUSER="sandorkazi"
GITHUBNAME="ansible-local-bootstrap"

INSTALLIT="???"
while [ "${INSTALLIT}" != "y" -a "${INSTALLIT}" != "n" ]; do
    echo -n "Do you want to start the installation after download? [y/n]: "; read -n1 INSTALLIT
    echo    ""
done

DISTRO=$(
    cat /etc/*-release \
    | sed -n -e 's/^ID=\(.*\)$/\1/p'
)

if [ "${DISTRO}" == "ubuntu" ]; then
    sudo apt install -y git
elif [ "${DISTRO}" == "manjaro" ]; then
    echo "Nothing to install"
else
    echo "Unknown DISTRO: ${DISTRO}"
fi

git clone "https://github.com/${GITUSER}/${GITHUBNAME}.git"

if [ "${INSTALLIT}" == "n" ]; then
    exit 0
else
    cd "${GITHUBNAME}"
    ./tools/prerequisites.sh
    ./tools/bootstrap.sh
    cd -
fi
