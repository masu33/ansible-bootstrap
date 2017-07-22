#!/usr/bin/env bash

############
# PLAYBOOK start for local desktop machine
# ----------
if [ -d ansible ] ; then
    ansible-playbook ./ansible/desktop.yml -i ./ansible/vagrant $@
elif [ -d ../ansible ] ; then
    ansible-playbook ../ansible/desktop.yml -i ../ansible/vagrant $@
else
    echo "This should be run from the project folder or the tools folder in it."
fi
