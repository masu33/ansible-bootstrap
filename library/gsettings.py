#!/usr/bin/env python
# coding=utf-8
"""
This module implements an Ansible module to get access to the gettings application.
"""

import json
import subprocess

from ansible.module_utils.basic import AnsibleModule
from ansible.errors import AnsibleOptionsError
from ansible.errors import AnsibleModuleError

import sys

__author__ = "Sandor Kazi"
__copyright__ = "Copyright 2016, ansible-desktop-bootstrap project"
__credits__ = ["Sandor Kazi", "Jiri Stransky"]
############
#  Before deciding to write this module the module of Jiri Stransky designed for very similar purposes was used, so this
#  might as well have similar parts. That's why his name is included in the credits.
#    - https://github.com/jistr/ansible-gsetting
############
__license__ = "GNU GPL3"
__maintainer__ = "Sandor Kazi"
__email__ = "givenname.familyname_AT_gmail.com"
__status__ = "Development"


class AnsibleGSettingModule(object):
    """
    Ansible module to change gsetting parameters for a given user.
    """

    UNKNOWN_IN_CHECK_MODE = ' - ??? - '
    """
    Value displayed when the actual "would be" result is unknown due to check mode.
    """

    __commands_for_dbus = """
            PID=$(pgrep gnome-session)
            export DBUS_SESSION_BUS_ADDRESS=$(
                sed -z -n -e 's/^DBUS_SESSION_BUS_ADDRESS=\(.*\)$/\\1/p' /proc/${PID}/environ
                )
            """
    """
    Internal commands to set DBUS parameters before calling gsettings.
    """

    @classmethod
    def __execute_su(cls, user, command):
        # type: (str, str, **Dict[str, str]) -> str
        """
        Executes a given command with the `user` used as username and returns its output.
        :param user: username
        :param command: command to execute
        :return: execution output
        :rtype: str
        """
        return subprocess.check_output([
            'sudo', 'su', '-', user, '-c', cls.__commands_for_dbus + command
        ]).strip()

    @classmethod
    def get_param(cls, user, schema, key):
        # type: (str, str, str) -> str
        """
        Gets the `user`'s gsetting value for the given `key` in the given `schema`.
        :param user: username
        :param schema: schema name
        :param key: key identifier
        :return: value as a string
        :rtype: str
        """
        command = "/usr/bin/gsettings get {} {}".format(schema, key)
        return cls.__execute_su(user, command)

    @classmethod
    def set_param(cls, user, schema, key, value):
        # type: (str, str, str, str) -> str
        """
        Sets the `user`'s gsetting value to the `value` specified for the given `key` in the given `schema` and returns
        the new value.
        :param user: username
        :param schema: schema name
        :param key: key identifier
        :param value: value as a string
        """
        value = value.replace("'", r"\'")
        if value in ['True', 'False']:
            value = value.lower()
        command = "/usr/bin/gsettings set {} {} '{}'".format(schema, key, value)
        cls.__execute_su(user, command)
        return value

    @classmethod
    def reset_param(cls, user, schema, key):
        # type: (str, str, str) -> str
        """
        Resets the `user`'s gsetting value for the given `key` in the given `schema` and returns the new value.
        :param user: username
        :param schema: schema name
        :param key: key identifier
        """
        command = "/usr/bin/gsettings reset {} {}".format(schema, key)
        cls.__execute_su(user, command)

    @classmethod
    def main(cls, test=None):
        """
        Executes the given module command.
        """

        # Normal (Ansible) call
        if test is None:
            # Module specs
            module = AnsibleModule(
                argument_spec={
                    'user': {'required': True},
                    'schema': {'required': True},
                    'key': {'required': True},
                    'value': {'required': False},
                    'state': {'choices': ['present',
                                          'absent'],
                              'default': 'present'
                              },
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
                        value = cls.set_param(user, schema, key, new_value)

                elif state == 'absent':
                    cls.reset_param(user, schema, key)

                else:
                    # shouldn't really happen without changing the module specs
                    raise NotImplementedError()

                new_value = cls.get_param(user, schema, key)
                if 'state' == 'present' and new_value.strip("'") != value.strip("'"):
                    raise AnsibleModuleError('Value not set...')
                changed = old_value.strip("'") != new_value.strip("'")

        print json.dumps({
            'changed': changed,
            'schema': schema,
            'key': key,
            'new_value': new_value,
            'old_value': old_value,
        })


if __name__ == '__main__':
    AnsibleGSettingModule.main(
        # {
        #     'check_mode': False,
        #     'params': {
        #         'state': 'present',
        #         'user': 'masu',
        #         'schema': 'com.canonical.indicator.session',
        #         'key': 'show-real-name-on-panel',
        #         'value': 'true',
        #     },
        # }
    )
