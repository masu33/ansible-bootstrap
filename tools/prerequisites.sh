#!/bin/bash

#############
# INSTALL ansible
# -----------
sudo apt-get update
sudo apt-get install python-setuptools \
                     build-essential \
                     autoconf \
                     libtool \
                     pkg-config \
                     python-dev \
                     libffi-dev \
                     libssl-dev \
                     aptitude \
                     git \
                     <<< "y"
sudo easy_install greenlet
sudo easy_install gevent
sudo easy_install pip
sudo pip2 install paramiko \
                 PyYAML \
                 Jinja2 \
                 httplib2 \
                 six \
                 git+https://github.com/ansible/ansible.git@devel
sudo mkdir /etc/ansible
