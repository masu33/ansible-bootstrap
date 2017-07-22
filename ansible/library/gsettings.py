#!/usr/bin/env python
# coding=utf-8
"""
This module implements an Ansible module to get access to the gettings application.
"""

import os
import signal
import subprocess

from abc import ABCMeta, abstractmethod, abstractproperty
from ansible.module_utils.basic import AnsibleModule
from gi.repository import GLib

__author__ = "Sandor Kazi"
__copyright__ = "Copyright 2016, ansible-desktop-bootstrap project"
__credits__ = ["Sandor Kazi"]
__license__ = "GNU GPL3"
__maintainer__ = "Sandor Kazi"
__email__ = "givenname.familyname_AT_gmail.com"
__status__ = "Development"


def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


class AnsibleGSettingModule(object):
    """
    Ansible module to change gsetting parameters for a given user.
    """

    def __init__(self):
        self.enabled = None
        self.dbus_pid = None
        self.dbus_address = None
        self.user = None
        self.variant_type = None
        self.variant_class = Variant

    def __destruct(self):
        """
        Kill DBUS created and remove xhost privileges if necessary.
        """
        if self.enabled == "0":
            subprocess.check_output('''
                DISPLAY=:1 sudo xhost -SI:localuser:{user}
                '''.format(user=self.user),
                                    shell=True
                                    )
        if self.dbus_pid is not None:
            try:
                os.kill(int(self.dbus_pid), signal.SIGTERM)
            except OSError:
                pass
        self.enabled = None
        self.dbus_pid = None
        self.dbus_address = None
        self.user = None

    def __init_dbus(self, user):
        """
        Initializes the message bus.

        :param user: username
        """
        self.user = user
        dbus_output = subprocess.check_output('''
            sudo -H -s /bin/bash -c "xhost +SI:localuser:{user}"
            sudo -H -u {user} -s /bin/bash -c "/usr/bin/dbus-launch"
            '''.format(
            user=user
        ),
            shell=True
        )
        for line in dbus_output.split('\n'):
            if line.startswith('DBUS_SESSION_BUS_ADDRESS='):
                self.dbus_address = line.split('=', 1)[1]
            elif line.startswith('DBUS_SESSION_BUS_PID='):
                self.dbus_pid = line.split('=', 1)[1]
        if self.dbus_address is None or self.dbus_pid is None:
            raise IOError('Error launching DBUS')

    def __execute(self, user, command):
        """
        Executes a given command with the `user` used as username and returns its output.

        :param user: username
        :param command: command to execute
        :return: command output
        :rtype: str
        """
        if self.dbus_pid is None:
            self.__init_dbus(user)
        shell_command = '''
            export DBUS_SESSION_BUS_ADDRESS={dbus_address}
            export DBUS_SESSION_BUS_PID={dbus_pid}
            sudo -H -u {user} -s /bin/bash -c "{command}"
            '''.format(
            dbus_address=self.dbus_address,
            dbus_pid=self.dbus_pid,
            user=user,
            command=command.replace('"', r'\"')
        )
        return subprocess.check_output(shell_command, shell=True).strip()

    def get_range_string(self, user, schema, path, key):
        """
        Gets the range of the `user`'s gsetting for the given `schema` and `key`.

        :param user: username
        :param schema: schema name
        :param path: path for relocatable schemas
        :param key: key identifier
        :return: command output
        :rtype: str
        """
        command = "/usr/bin/gsettings range {schema}{colon}{path} {key}".format(
            schema=schema,
            colon='' if path is None else ':',
            path='' if path is None else path,
            key=key
        )
        output = self.__execute(user, command).replace('\n', ' ').replace('\r', ' ')
        return output

    def get_param(self, user, schema, path, key):
        """
        Gets the `user`'s gsetting value for the given `key` in the given `schema`.

        :param user: username
        :param schema: schema name
        :param path: path for relocatable schemas
        :param key: key identifier
        :return: command output
        :rtype: Variant
        """
        command = "/usr/bin/gsettings get {schema}{colon}{path} {key}".format(
            schema=schema,
            colon='' if path is None else ':',
            path='' if path is None else path,
            key=key
        )
        output = self.__execute(user, command)
        return self.variant_class(self.variant_type, output)

    def get_default(self, user, schema, path, key):
        """
        Gets the default gsetting value for the given `key` in the given `schema`.

        :param user: username
        :param schema: schema name
        :param path: path for relocatable schemas
        :param key: key identifier
        :return: command output
        :rtype: Variant
        """
        command = "XDG_CONFIG_HOME=/nonexistent /usr/bin/gsettings get {schema}{colon}{path} {key}".format(
            schema=schema,
            colon='' if path is None else ':',
            path='' if path is None else path,
            key=key
        )
        output = self.__execute(user, command)
        return self.variant_class(self.variant_type, output)

    def set_param(self, user, schema, path, key, value):
        """
        Sets the `user`'s gsetting value to the `value` specified for the given `key` in the given `schema` and
        returns the new value.

        :param user: username
        :param schema: schema name
        :param path: path for relocatable schemas
        :param key: key identifier
        :param value: value as a string
        :return: command output
        :rtype: str
        """
        command = (
            '/usr/bin/gsettings set {schema}{colon}{path} {key} "{value}"'.format(
                schema=schema,
                colon='' if path is None else ':',
                path='' if path is None else path,
                key=key,
                value=value.replace('"', r'\"')
            )
        )
        output = self.__execute(user, command)
        return output

    def reset_param(self, user, schema, path, key):
        """
        Resets the `user`'s gsetting value for the given `key` in the given `schema` and returns the new value.

        :param user: username
        :param schema: schema name
        :param path: path for relocatable schemas
        :param key: key identifier
        :return: command output
        :rtype: str
        """
        command = '/usr/bin/gsettings reset {schema}{colon}{path} {key}'.format(
            schema=schema,
            colon='' if path is None else ':',
            path='' if path is None else path,
            key=key
        )
        output = self.__execute(user, command)
        return output

    def __setup_class(self, user, schema, path, key, range_string=None):
        if range_string is None:
            range_string = self.get_range_string(user, schema, path, key)

        range_type, range_desc = range_string.split(' ', 1)
        if range_type == 'type':
            self.variant_type = range_desc
        elif range_type == 'flags':
            self.variant_type = 'as'
        elif range_type == 'range':
            self.variant_type = range_desc[0]
        elif range_type == 'enum':
            self.variant_type = 's'
        else:
            raise NotImplementedError('Unknown range type: {}'.format(range_string))

    def __use_type(self, value):
        return self.variant_class(self.variant_type, value)

    def main(self):
        """
        Executes the given module command.
        """

        # Module specs
        m = AnsibleModule(
            argument_spec={
                'user':      {'required': True},
                'schema':    {'required': True},
                'path':      {'required': False, 'default': None},
                'key':       {'required': True},
                'value':     {'required': False, 'default': None},
                'state':     {'required': False, 'default': 'present', 'choices': ['present', 'absent']},
                'set_type':  {'required': False, 'default': False, 'choices': [True, False]},
                'range':     {'required': False, 'default': None},
            },
            supports_check_mode=True,
        )

        # Parameters
        params = m.params
        user = params.get('user')
        schema = params.get('schema')
        path = params.get('path')
        key = params.get('key')
        value = params.get('value')
        state = params.get('state')
        set_type = params.get('set_type')
        range_string = params.get('range_string')

        # Check mode
        check_mode = m.check_mode

        # Error check
        if state == 'present' and value is None:
            raise ValueError('The value parameter have to be set with the state "present".')

        self.__setup_class(user, schema, path, key, range_string)

        default = self.get_default(user, schema, path, key)
        value_before = self.get_param(user, schema, path, key)

        if set_type:

            if not default.is_container():
                raise('The `composite` argument can only be used for collections, not {}.'.format(self.variant_type))

            else:
                value_wanted = 2

        else:

            value = {
                'present': value,
                'absent': default
            }[state]

            value_wanted = self.__use_type(value)

        if check_mode:

            value_after = value_wanted
            changed = not value_before == value_after

        else:

            if value_wanted == value_before:

                changed = False
                value_after = value_before

            elif value_wanted == default:

                self.reset_param(user, schema, path, key)
                changed = True
                value_after = self.get_param(user, schema, path, key)

            else:

                self.set_param(user, schema, path, key, value_wanted)
                changed = True
                value_after = self.get_param(user, schema, path, key)

            if value_after != value_wanted:
                raise ValueError('Unknown error, value change mismatch...')

        m.exit_json(
            changed=changed,
            user=user,
            schema=schema,
            path=path,
            key=key,
            value_before=str(value_before),
            value_after=str(value_after),
        )


class Variant(object):

    def __convert(self, value):
        return GLib.Variant.parse(self.type, value, '\n', '\n')

    def __init__(self, type_string, value, encode=False):
        if not GLib.variant_type_string_is_valid(type_string):
            raise ValueError('Invalid type string {}'.format(type_string))

        self.type = GLib.VariantType.new(type_string)
        self.value = self.__convert(value)

    def __encode(self, obj):
        raise NotImplementedError()

    def __encode_item(self, obj):
        raise NotImplementedError()

    def __present(self, item):
        if not isinstance(item, str):
            raise NotImplementedError('Value must be string, not {}.'.format(type(item)))
        item = self.__convert('[{}]'.format(item))
        if item[0] not in self.value:
            self.value = self.__convert(str(list(item) + list(self.value)))

    def __absent(self, item):
        if not isinstance(item, str):
            raise NotImplementedError('Value must be string, not {}.'.format(type(item)))
        item = self.__convert('[{}]'.format(item))
        if item[0] in self.value:
            self.value = self.__convert(str([i for i in list(self.value) if i != item[0]]))

    def __eq__(self, other):
        return str(self) == str(other)

    def __ne__(self, other):
        return str(self) != str(other)

    def __repr__(self):
        return str(self.value)

    def is_container(self):
        return self.value.is_container()

    def replace(self, *args, **kwargs):
        return str(self).replace(*args, **kwargs)


if __name__ == '__main__':
    AnsibleGSettingModule().main()
