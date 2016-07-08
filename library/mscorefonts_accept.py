#!/usr/bin/env python
# coding=utf-8
"""
This module implements an Ansible module to accept the license for ttf-mscorefonts-installer package if necessary.
"""

import subprocess

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


class AnsibleMSCoreFontsModule(object):
    """
    Ansible module to accept the license for ttf-mscorefonts-installer package if necessary.
    """

    @staticmethod
    def __check_package(cls, package):
        # type: (str) -> bool
        """
        Check whether the package is already installed.
        :param package:
        :return:
        """
        raise NotImplementedError()

    @staticmethod
    def __accept_eula():
        """
        Accept the MS EULA to install the package.
        """
        command = [
            'echo',
            'ttf-mscorefonts-installer',
            'msttcorefonts/accepted-mscorefonts-eula select true',
            '|',
            'sudo',
            'debconf-set-selections',
        ]
        return subprocess.check_output(command).strip()

    @classmethod
    def main(cls):
        """
        Executes the given module command.
        """

        # Normal (Ansible) call
        if test is None:
            # Module specs
            module = AnsibleModule(
                argument_spec={
                    'state': {'choices': ['present'], 'default': 'present'},
                },
                supports_check_mode=True,
            )

            # Parameters
            params = module.params
            user = params.get('user')
            schema = params.get('schema')
            key = params.get('key')
            new_value = params.get('value')
            state = params.get('state')

            # Check mode
            check_mode = module.check_mode

        # Test call
        else:
            # Parameters
            params = test.get('params', {})
            user = params.get('user')
            schema = params.get('schema')
            key = params.get('key')
            new_value = params.get('value')
            state = params.get('state')

            # Check mode
            check_mode = test.get('check_mode')

        # Handling option errors
        if state == 'present' and new_value is None:
            raise AnsibleOptionsError('The value parameter should be set when using the state "present".')
        elif state == 'absent' and new_value is not None:
            raise AnsibleOptionsError('The value parameter should not be set when using the state "absent".')

        # Operation logic
        else:
            old_value = cls.get_param(user, schema, key)

            if check_mode:
                new_value = cls.UNKNOWN_IN_CHECK_MODE
                changed = False

            else:

                if state == 'present':
                    # change only if it's necessary
                    if old_value.strip("'") != new_value.strip("'"):
                        new_value = cls.set_param(user, schema, key, new_value)
                    current_value = cls.get_param(user, schema, key)

                    if new_value.strip("'") != current_value.strip("'"):
                        raise AnsibleModuleError('Value not set...')
                    else:
                        new_value = current_value

                elif state == 'absent':
                    cls.reset_param(user, schema, key)
                    new_value = cls.get_param(user, schema, key)

                else:
                    # shouldn't really happen without changing the module specs
                    raise NotImplementedError()

                changed = old_value.strip("'") != new_value.strip("'")

        print json.dumps({
            'changed': changed,
            'schema': schema,
            'key': key,
            'new_value': new_value,
            'old_value': old_value,
        })


if __name__ == '__main__':
    AnsibleMSCoreFontsModule.main()
