#!/bin/bash

PASS=`python -c "from passlib.hash import sha512_crypt; import getpass; print sha512_crypt.using(rounds=5000).hash(getpass.getpass())"`

ansible-vault encrypt_string "${PASS}" $@

