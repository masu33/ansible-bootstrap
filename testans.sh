#!/bin/bash

ansible localhost -i ansible/ug -m gsettings -M ansible/library --args "user=masu schema=org.gnome.gedit.plugins.filebrowser key=filter-mode value=hide-hidden state=absent set_type=True"
