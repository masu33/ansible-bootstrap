#!/bin/bash

# TEST root
if [ "$(id -u)" != "0" ]; then
  echo "Sorry, you are not root."
  exit 1
fi

# INSTALL ansible
apt-get install python-setuptools build-essential autoconf libtool pkg-config python-dev python-apt libffi-dev libssl-dev aptitude <<< "y"
easy_install greenlet
easy_install gevent
easy_install pip
pip install paramiko PyYAML Jinja2 httplib2 six ansible
sudo mkdir /etc/ansible
echo -e "localhost\tansible_connection=local\n" > /etc/ansible/hosts

