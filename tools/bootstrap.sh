#!/usr/bin/env bash

PROOT=`git rev-parse --show-toplevel`
ansible-playbook -K ${PROOT}/ansible/desktop.yml -i ${PROOT}/ansible/localhost --ask-vault-pass $@
