#!/usr/bin/env bash

############
# PLAYBOOK start for local desktop machine
# ----------
alias python=python2

if [[ "${DISPLAY}" == "" ]]; then
    echo "Please set DISPLAY for the visual settings!"
    echo -n "    DISPLAY="
    read DISPLAY
    export DISPLAY
fi

./library/prerequisites.sh
ansible-playbook -K masu-desktop.yml -i localhost
