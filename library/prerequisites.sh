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

############
# START ansible raw on remote host
# ----------
ansible $1 --sudo -m raw -a "yum install -y python2 python-simplejson"

