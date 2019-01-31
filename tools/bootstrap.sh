#!/usr/bin/env bash

ROOT=`git rev-parse --show-toplevel`/ansible

cd $ROOT
ansible-playbook $@ -K -i ${ROOT}/local.inventory ${ROOT}/main.yml
