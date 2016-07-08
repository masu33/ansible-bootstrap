#!/bin/bash

############
# Overview:
#   TODO
# ----------
# Author:
#   TODO
# ----------
# Description:
#   TODO
# ----------
# Usage:
#   TODO
# ----------
# Notes:
#   TODO
############

#############
# INSTALL ansible
# -----------
sudo apt-get install python-setuptools \
                     build-essential \
                     autoconf \
                     libtool \
                     pkg-config \
                     python-dev \
                     python-apt \
                     libffi-dev \
                     libssl-dev \
                     aptitude <<< "y"
sudo easy_install greenlet
sudo easy_install gevent
sudo easy_install pip
sudo pip install paramiko \
                 PyYAML \
                 Jinja2 \
                 httplib2 \
                 six \
                 ansible
sudo mkdir /etc/ansible

############
# PLAYBOOK start for local desktop machine
# ----------
ansible-playbook -K desktop.yml -i local_desktop -vvv

