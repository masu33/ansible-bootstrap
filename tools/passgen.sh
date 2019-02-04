#!/bin/bash
# For generating passwords to be stored as a vault variable

SILENCER="-s"
PRINTED_NEWLINE="\n"
if [ "$SHOW" != "" ]; then
    SILENCER=""
    PRINTED_NEWLINE=""
fi

echo -n -e "Enter secret (1): "; read $SILENCER STRING1; echo -n $PRINTED_NEWLINE
echo -n -e "Enter secret (2): "; read $SILENCER STRING2; echo -n $PRINTED_NEWLINE

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
if [ $NOSHA == "" ]; then
    SECRET=`python -c "$PYCOMMAND"`
else
    SECRET=$STRING1
fi

if [ "$STRING1" == "$STRING2" ]; then
    ansible-vault encrypt_string $EXTRA "$SECRET"
else
    echo "Strings do not match!"
fi
