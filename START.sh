#!/usr/bin/env bash

############
# PLAYBOOK start for local desktop machine
# ----------
alias python=python2
./library/prerequisites.sh
ansible-playbook -K desktop.yml -i local_desktop -vvv