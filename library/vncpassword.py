#!/usr/bin/env python
# coding=utf-8
"""
This module implements an Ansible module to set VNC passwords.
"""

import filecmp
import json
import os
import pwd
import shutil
import subprocess
import tempfile

from ansible.module_utils.basic import AnsibleModule
from ansible.errors import AnsibleOptionsError
from ansible.errors import AnsibleModuleError

__author__ = "Sandor Kazi"
__copyright__ = "Copyright 2016, ansible-desktop-bootstrap project"
__credits__ = ["Sandor Kazi"]
__license__ = "GNU GPL3"
__maintainer__ = "Sandor Kazi"
__email__ = "givenname.familyname_AT_gmail.com"
__status__ = "Development"


def _temp_file(mode=0o600, retries=10):
    for i in range(retries):
        tmp = tempfile.mktemp(dir=tempfile.gettempdir())
        if not os.path.exists(tmp):
            with os.fdopen(os.open(tmp, os.O_WRONLY | os.O_CREAT, mode), 'w') as handle:
                handle.write('')
            return tmp
    raise AnsibleModuleError('Could not create temporary file.')


class AnsibleVNCPasswordModule(object):
    """
    Ansible module to set or reset VNC password for the executor.
    """

    @staticmethod
    def get_file(path):
        with open(path, 'rb') as handle:
            return bytearray(handle)

    @staticmethod
    def set_password(password, path):
        tmp = _temp_file()
        with os.fdopen(os.open(tmp, os.O_WRONLY | os.O_CREAT, 0o700), 'w') as handle:
            handle.write(password)
            handle.write('\n')
            handle.write(password)
        result = subprocess.check_output('''
            vncpasswd {path} < {tmpfile} | sed -e 's/^Password:Verify:$//'
            '''.format(
                path=path,
                tmpfile=tmp,
            ),
            shell=True,
        ).strip()
        os.unlink(tmp)
        return result

    def main(self):
        """
        Executes the given module command.
        """

        # Module specs
        module = AnsibleModule(
            argument_spec={
                'password': {'required': False},
                'path':     {'required': True},
                'state':    {'required': False, 'default': 'present', 'choices': ['present', 'absent']},
            },
            supports_check_mode=True,
        )

        # Parameters
        params = module.params
        password = params.get('password')
        path = params.get('path')
        state = params.get('state')

        # Check mode
        check_mode = module.check_mode

        # Error check
        if state == 'present':
            if password is None:
                raise AnsibleOptionsError('The password parameter have to be set with the state "present".')
        elif state == 'absent':
            if password is not None:
                raise AnsibleOptionsError('The parameter parameter should not be set when using the state "absent".')

        if os.path.exists(path) and not os.path.isfile(path):
            raise AnsibleModuleError('Supplied path exists but is not a file.')

        try:

            if state == 'present':
                if os.path.exists(path):
                    tmp = _temp_file()
                    self.set_password(password, tmp)
                    changed = not filecmp.cmp(tmp, path, 0)
                    if not check_mode and changed:
                        shutil.copy(tmp, path)
                    os.unlink(tmp)
                else:
                    if not check_mode:
                        dir = os.path.dirname(path)
                        if not os.path.exists(dir) or not os.path.isdir(dir):
                            os.makedirs(dir)
                        self.set_password(password, path)
                    changed = True
            elif state == 'absent':
                if os.path.exists(path):
                    if not check_mode:
                        os.unlink(path)
                    changed = True
                else:
                    changed = False
            else:
                raise NotImplementedError('Unknown state')  # This should not happen

        except OSError:
            raise AnsibleModuleError('Unable to manipulate path.')

        print json.dumps({
            'changed': changed,
            'path': path,
        })

if __name__ == '__main__':
    AnsibleVNCPasswordModule().main()
