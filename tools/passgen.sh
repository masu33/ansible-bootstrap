#!/bin/bash
# For generating passwords to be stored as a vault variable

echo -n -e "Enter secret (1): "; read -s STRING1; echo
echo -n -e "Enter secret (2): "; read -s STRING2; echo

if [ "$1" != "" ]; then
    EXTRA=" --vault-id $1"
else
    EXTRA=""
fi

PYCOMMAND="
from passlib.hash import sha512_crypt
import getpass
print(sha512_crypt.using(rounds=5000).hash('$STRING1'))
"

if [ "$STRING1" == "$STRING2" ]; then
    HASH=`python -c "$PYCOMMAND"`
    ansible-vault encrypt_string $EXTRA "$HASH"
else
    echo "Strings do not match!"
fi
