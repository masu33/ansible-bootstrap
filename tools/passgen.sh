#!/bin/bash
# For generating passwords to be stored as a vault variable

PASS=`python -c "from passlib.hash import sha512_crypt; import getpass; print sha512_crypt.using(rounds=5000).hash(getpass.getpass())"`

ansible-vault encrypt_string "${PASS}" $@

