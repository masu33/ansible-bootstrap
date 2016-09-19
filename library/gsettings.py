#!/usr/bin/env python
# coding=utf-8
"""
This module implements an Ansible module to get access to the gettings application.
"""

import json
import subprocess
import os
import signal

from ansible.module_utils.basic import AnsibleModule
from ansible.errors import AnsibleOptionsError
from ansible.errors import AnsibleModuleError

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

    def __init__(self):
        self.enabled = None
        self.dbus_pid = None
        self.dbus_address = None
        self.user = None

    def __destruct(self):
        """
        Kill DBUS created and remove xhost privileges if necessary.
        """
        if self.enabled == "0":
            subprocess.check_output('''
                sudo xhost -SI:localuser:{user}
                '''.format(user=self.user),
                shell=True
            )
        if self.dbus_pid is not None:
            try:
                os.kill(int(self.dbus_pid), signal.SIGTERM)
            except OSError:
                pass

    def __init_dbus(self, user):
        # type: (str)
        """
        Initializes the message bus.
        :param user: username
        """
        self.user = user
        dbus_output = subprocess.check_output('''
            export DISPLAY=:0
            ENABLED=$(sudo xhost | grep -c "SI:localuser:{user}")
            echo "ENABLED=$ENABLED"
            sudo xhost +SI:localuser:{user}
            sudo -H -u {user} -s /usr/bin/dbus-launch
            '''.format(user=user),
            shell=True
        )
        for line in dbus_output.split('\n'):
            if line.startswith('DBUS_SESSION_BUS_ADDRESS='):
                self.dbus_address = line.split('=', 1)[1]
            elif line.startswith('DBUS_SESSION_BUS_PID='):
                self.dbus_pid = line.split('=', 1)[1]
            elif line.startswith('ENABLED='):
                self.enabled = line.split('=', 1)[1]

    def __execute(self, user, command):
        # type: (str, str) -> str
        """
        Executes a given command with the `user` used as username and returns its output.
        :param user: username
        :param command: command to execute
        :return: execution output
        :rtype: str
        """
        if self.dbus_pid is None:
            self.__init_dbus(user)
        gset = subprocess.check_output('''
            export DISPLAY=:0
            export DBUS_SESSION_BUS_ADDRESS={dbus_address}
            export DBUS_SESSION_BUS_PID={dbus_pid}
            sudo -H -u {user} -s /bin/bash -c \'{command}\'
            '''.format(dbus_address=self.dbus_address, dbus_pid=self.dbus_pid, user=user, command=command),
            shell=True
        ).strip()
        return gset

    def get_param(self, user, schema, key):
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
        return self.__execute(user, command)

    def set_param(self, user, schema, key, value):
        # type: (str, str, str, str) -> str
        """
        Sets the `user`'s gsetting value to the `value` specified for the given `key` in the given `schema` and returns
        the new value.
        :param user: username
        :param schema: schema name
        :param key: key identifier
        :param value: value as a string
        """
        if value in ['true', 'false']:
            command = "/usr/bin/gsettings set {} {} {}".format(schema, key, value)
        else:
            command = "/usr/bin/gsettings set {} {} '{}'".format(schema, key, value)
        self.__execute(user, command)
        return value

    def reset_param(self, user, schema, key):
        # type: (str, str, str) -> str
        """
        Resets the `user`'s gsetting value for the given `key` in the given `schema` and returns the new value.
        :param user: username
        :param schema: schema name
        :param key: key identifier
        """
        command = "/usr/bin/gsettings reset {} {}".format(schema, key)
        self.__execute(user, command)

    def main(self, test=None):
        # type: (dict) -> None
        """
        Executes the given module command.
        :type test: dictionary object for testing purposes only
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
            old_value = self.get_param(user, schema, key)

            if check_mode:
                new_value = self.UNKNOWN_IN_CHECK_MODE
                changed = False

            else:

                if state == 'present':
                    new_value = new_value.strip("'")
                    if new_value in ['True', 'False']:
                        new_value = new_value.lower()
                    # change only if it's necessary
                    if old_value.strip("'") != new_value.strip("'"):
                        new_value = self.set_param(user, schema, key, new_value)
                    current_value = self.get_param(user, schema, key)

                    if new_value.strip("'") != current_value.strip("'"):
                        raise AnsibleModuleError('Value not set...')
                    else:
                        new_value = current_value

                elif state == 'absent':
                    self.reset_param(user, schema, key)
                    new_value = self.get_param(user, schema, key)

                else:
                    # shouldn't really happen without changing the module specs
                    raise NotImplementedError()

                changed = old_value.strip("'") != new_value.strip("'")

        self.__destruct()

        print json.dumps({
            'changed': changed,
            'schema': schema,
            'key': key,
            'new_value': new_value,
            'old_value': old_value,
        })


if __name__ == '__main__':
    AnsibleGSettingModule().main()
