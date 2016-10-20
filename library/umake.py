#!/usr/bin/env python
# coding=utf-8
"""
This module implements an Ansible module to use ubuntu-make.
"""

import json
import subprocess
import os
import yaml

from ansible.module_utils.basic import AnsibleModule
from ansible.errors import AnsibleOptionsError

__author__ = "Sandor Kazi"
__copyright__ = "Copyright 2016, ansible-desktop-bootstrap project"
__credits__ = ["Sandor Kazi"]
__license__ = "GNU GPL3"
__maintainer__ = "Sandor Kazi"
__email__ = "givenname.familyname_AT_gmail.com"
__status__ = "Development"


class AnsibleUMakeModule(object):
    """
    Ansible module to use ubuntu-make.
    """

    CONFIG_LOCATION = '~/.config/umake'
    DEFAULT_LOCATION = '~/.local/share/umake'

    def __location(self, category, framework):
        """
        Returns the current location of the framework specified.
        :param category: ubuntu-make command
        :param framework: ubuntu-make item
        :return: path where it is currently installed or None
        """
        try:
            return yaml.load(file(os.path.expanduser(self.CONFIG_LOCATION)))['frameworks'][category][framework]['path']
        except (IndexError, KeyError, IOError):
            return None

    def __execute(self, command):
        """
        Executes a given command.
        :param command: command to executre
        :return: output produced
        """
        output = subprocess.check_output(
            command,
            shell=True
        ).strip()
        return output

    def main(self):
        """
        Executes the given module command.
        """

        # Module specs
        module = AnsibleModule(
            argument_spec={
                'executable': {'default': 'umake'},
                'category': {'required': True},
                'framework': {'required': True},
                'path': {'default': None},
                'state': {
                    'choices': ['absent', 'present'],
                    'default': 'present',
                },
            },
            supports_check_mode=True,
        )

        # Parameters
        params = module.params
        category = params.get('category')
        framework = params.get('framework')
        path = params.get('path')
        state = params.get('state')

        # Check mode
        check_mode = module.check_mode

        # Handling option errors
        if state == 'absent' and path is not None:
            raise AnsibleOptionsError('You can\'t specify a destination dir while removing a framework')

        # Operation logic
        else:
            switch = ' '
            if state == 'absent':
                path = ''
                switch = ' -r'
            elif path is None:
                path = os.path.abspath(
                    os.path.expanduser(
                        '{}/{}/{}'.format(
                            self.DEFAULT_LOCATION,
                            category,
                            framework
                        )
                    )
                )

            old_path = self.__location(category, framework)

            command = '''yes "no" | umake {category} {framework}{switch}{path}'''.format(
                category=category,
                framework=framework,
                switch=switch,
                path=path,
            )

            changed = (
                (state == 'present' and old_path is None) or
                (state == 'present' and old_path != path) or
                (state == 'absent' and old_path is not None)
            )

            if check_mode:
                pass
            else:
                if changed:
                    self.__execute(command)
                else:
                    pass

        print json.dumps({
            'changed': changed,
            'command': command,
            'old_path': old_path,
            'new_path': path,
        })

if __name__ == '__main__':
    AnsibleUMakeModule().main()
