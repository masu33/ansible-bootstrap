#!/usr/bin/env bash

PROOT=`git rev-parse --show-toplevel`

script -q -c "ansible-playbook \
    -K ${PROOT}/ansible/main.yml \
    -i ${PROOT}/ansible/localhost \
    --ask-vault-pass $@" \
    "${PROOT}/ansible/logs/last.log"
