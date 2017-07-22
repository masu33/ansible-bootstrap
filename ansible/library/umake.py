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
    DEFAULT_ROOT = '~/.local/share/umake'

    def __location(self, user, category, framework):
        """
        Returns the current location of the framework specified.
        :param category: ubuntu-make command
        :param framework: ubuntu-make item
        :return: path where it is currently installed or None
        """
        try:
            return yaml.load(
                file(
                    os.path.expanduser(
                        self.CONFIG_LOCATION.replace('~/', '~{}/'.format(user))
                    )
                )
            )['frameworks'][category][framework]['path']
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
                'user': {'required': False},
                'category': {'required': True},
                'framework': {'required': True},
                'path': {'default': None},
                'state': {
                    'choices': ['absent', 'present', 'latest'],
                    'default': 'present',
                },
            },
            supports_check_mode=True,
        )

        # Parameters
        params = module.params
        executable = params.get('executable')
        user = params.get('user')
        category = params.get('category')
        framework = params.get('framework')
        path = params.get('path')
        state = params.get('state')

        # Check mode
        check_mode = module.check_mode

        # Operation logic
        switch = ' '
        if state == 'absent':
            path = ''
            switch = ' -r'
        elif path is None:
            path = os.path.abspath(
                '{}/{}/{}'.format(
                    os.path.expanduser(self.DEFAULT_ROOT.replace('~/', '~{}/'.format(user))),
                    category,
                    framework
                )
            )

        old_path = self.__location(user, category, framework)

        command = '''
            sudo -s;
            unset SUDO_UID;
            unset SUDO_GID;
            sudo -u {user} yes "no" | {executable} {category} {framework}{switch} {path}'''.format(
            user=user,
            executable=executable,
            category=category,
            framework=framework,
            switch=switch,
            path=path,
        )

        changed = (
            (state == 'present' and old_path is None) or
            (state == 'present' and old_path != path) or
            (state == 'absent'  and old_path is not None)
        )

        output = ''
        try:
            if check_mode:
                pass
            else:
                if changed:
                    with open('/tmp/umakelog', 'a') as f:
                        f.write('ABCA ' + command)
                    output = self.__execute(command)
                    with open('/tmp/umakelog', 'a') as f:
                        f.write('XYZX')
                else:
                    pass
        except Exception as e:
            with open('/tmp/umakelog', 'a') as f:
                f.write(e)
        finally:
            with open('/tmp/umakelog', 'a') as f:
                f.write(output)

        module.exit_json(
            changed=changed,
            command=command,
            old_path=old_path,
            new_path=path
        )

if __name__ == '__main__':
    AnsibleUMakeModule().main()
