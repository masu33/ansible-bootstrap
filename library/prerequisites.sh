#!/bin/bash
ansible $1 --sudo -m raw -a "yum install -y python2 python-simplejson"

