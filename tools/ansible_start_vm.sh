#!/usr/bin/env bash

############
# PLAYBOOK start for local desktop machine
# ----------
if [ -d ansible ] ; then
    ansible-playbook ./ansible/desktop.yml -i ./ansible/vm --ask-vault-pass $@
elif [ -d ../ansible ] ; then
    ansible-playbook ../ansible/desktop.yml -i ../ansible/vm --ask-vault-pass $@
else
    echo "This should be run from the project folder or the tools folder in it."
fi