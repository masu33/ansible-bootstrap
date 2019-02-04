#!/bin/bash

DISTRO=$(
    cat /etc/*-release \
    | sed -n -e 's/^ID=\(.*\)$/\1/p'
)

if [ "${DISTRO}" == "ubuntu" ]; then
    sudo apt update
    sudo apt install -y python3 python3-pip
    sudo pip3 install ansible jmespath
elif [ "${DISTRO}" == "manjaro" ]; then
    yes | sudo pacman -S python3
    sudo pip3 install ansible jmespath
elif [ "${DISTRO}" == "\"ol\"" ]; then
    sudo yum-config-manager --enable ol*_developer_EPEL
    sudo yum install -y python-pip
    sudo pip install ansible jmespath
else
    echo "Unknown DISTRO: ${DISTRO}"
    exit 1
fi
