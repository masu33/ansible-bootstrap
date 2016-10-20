#!/usr/bin/env python
# coding=utf-8
"""
This module implements an Ansible module to get access to the gettings application.
"""

import json
import os
import signal
import subprocess

from ansible.module_utils.basic import AnsibleModule
from ansible.errors import AnsibleOptionsError
from ansible.errors import AnsibleModuleError
from gi.repository import GLib

__author__ = "Sandor Kazi"
__copyright__ = "Copyright 2016, ansible-desktop-bootstrap project"
__credits__ = ["Sandor Kazi"]
__license__ = "GNU GPL3"
__maintainer__ = "Sandor Kazi"
__email__ = "givenname.familyname_AT_gmail.com"
__status__ = "Development"


class AnsibleGSettingModule(object):
    """
    Ansible module to change gsetting parameters for a given user.
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
            raise AnsibleModuleError('Error launching DBUS')

    def __execute(self, user, command):
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
            export DBUS_SESSION_BUS_ADDRESS={dbus_address}
            export DBUS_SESSION_BUS_PID={dbus_pid}
            sudo -H -u {user} -s /bin/bash -c "{command}"
            '''.format(
                dbus_address=self.dbus_address,
                dbus_pid=self.dbus_pid,
                user=user,
                command=command.replace('"', r'\"'),
            ),
            shell=True
        ).strip()
        return gset

    def get_type(self, user, schema, key):
        """
        Gets the type of the `user`'s gsetting value for the given `key` in the given `schema`.

        :param user: username
        :param schema: schema name
        :param key: key identifier
        :return: type as a string
        :rtype: str
        """
        command = "/usr/bin/gsettings range {} {}".format(schema, key)
        result = self.__execute(user, command)
        if result.startswith('type '):
            return result[5:]
        elif result.startswith('enum'):
            return 's'
        else:
            raise AnsibleModuleError('Not supported value type: {}'.format(result))

    def get_param(self, user, schema, key):
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

    def get_default(self, user, schema, key):
        """
        Gets the default gsetting value for the given `key` in the given `schema`.

        :param user: username
        :param schema: schema name
        :param key: key identifier
        :return: value as a string
        :rtype: str
        """
        command = "XDG_CONFIG_HOME=/nonexistent /usr/bin/gsettings get {} {}".format(schema, key)
        return self.__execute(user, command)

    def set_param(self, user, schema, key, value):
        """
        Sets the `user`'s gsetting value to the `value` specified for the given `key` in the given `schema` and
        returns the new value.

        :param user: username
        :param schema: schema name
        :param key: key identifier
        :param value: value as a string
        """
        if value in ['true', 'false']:
            command = '/usr/bin/gsettings set {} {} {}'.format(schema, key, value)
        else:
            command = '/usr/bin/gsettings set {} {} "{}"'.format(schema, key, value)
        self.__execute(user, command)
        return value

    def reset_param(self, user, schema, key):
        """
        Resets the `user`'s gsetting value for the given `key` in the given `schema` and returns the new value.

        :param user: username
        :param schema: schema name
        :param key: key identifier
        """
        command = '/usr/bin/gsettings reset {} {}'.format(schema, key)
        self.__execute(user, command)

    def main(self):
        """
        Executes the given module command.
        """

        # Module specs
        module = AnsibleModule(
            argument_spec={
                'user':   {'required': True},
                'schema': {'required': True},
                'key':    {'required': True},
                'value':  {'required': False, 'default': None},
                'state':  {'required': False, 'default': 'present', 'choices': ['present', 'absent']},
                'raw':    {'required': False, 'default': False,     'choices': [True, False]},
            },
            supports_check_mode=True,
        )

        # Parameters
        params = module.params
        user = params.get('user')
        schema = params.get('schema')
        key = params.get('key')
        value = params.get('value')
        state = params.get('state')
        raw = params.get('raw')

        # Check mode
        check_mode = module.check_mode

        gvar = _GVariantCreator(
            type_string=self.get_type(user, schema, key),
            default=self.get_default(user, schema, key),
            state=state,
            raw=raw,
        )

        # Error check
        if state == 'present':
            if value is None:
                raise AnsibleOptionsError('The value parameter have to be set with the state "present".')
        elif state == 'absent':
            if value is not None and not gvar.is_container:
                    raise AnsibleOptionsError(
                        'The value parameter should not be set when using the state "absent" on a literal.'
                    )

        value_before = gvar(self.get_param(user, schema, key))
        value_wanted = gvar(value, modifying=value_before)

        if check_mode:

            value_after = value_wanted
            changed = not value_before == value_after

        else:

            if value_before == value_wanted:

                value_after = value_before
                changed = False

            else:

                self.set_param(user, schema, key, value_wanted)
                value_after = gvar(self.get_param(user, schema, key))
                changed = True
                if value_after != value_wanted:
                    raise AnsibleModuleError('Unknown error, value has not been set...')

        print json.dumps({
            'changed': changed,
            'schema': schema,
            'key': key,
            'value': value,
            'value_before': str(value_before),
            'value_after': str(value_after),
        })

        self.__destruct()


class _GVariantCreator(object):

    @property
    def type(self):
        return self.__type

    @property
    def is_container(self):
        return self.__is_container

    def __parse(self, value):
        try:
            return GLib.variant_parse(GLib.VariantType(self.type), value)
        except GLib.Error:
            raise AnsibleModuleError('Could not parse GVariant (type: {}, value: {})'.format(self.type, value))

    def __call__(self, value, **kwargs):
        return self.__new(value, **kwargs)

    def __new(self, _, **__):
        raise NotImplementedError()

    def __new_(self, value, **_):
        return self.__parse(value)

    def __new_str(self, value, **_):
        return self.__parse('\'{}\''.format(str(value).strip('\'')))

    def __new_bool(self, value, **_):
        if value:
            return self.__parse('true')
        else:
            return self.__parse('false')

    def __new_list_present(self, value, modifying=None, **_):
        if modifying is None:
            return self.__parse(str(value))
        else:
            init = list(modifying)
            if value not in init:
                init.append(value)
            return self.__parse(str(init))

    def __new_list_absent(self, value, modifying=None, default=None, **_):
        if modifying is None:
            return self.__parse(value)
        elif value is None:
            return self.__parse(default)
        else:
            return self.__parse(str([i for i in list(modifying) if i != value]))

    def __init__(self, type_string, default, state, raw):
        self.__type = type_string
        try:
            gvar = GLib.variant_parse(GLib.VariantType(type_string), default)
        except TypeError:
            raise AnsibleModuleError('Could not parse def. GVariant (type: {}, value: {})'.format(self.type, default))
        self.__is_container = gvar.is_container()

        if not raw:
            if state == 'present':
                if self.type == 's':  # string
                    self.__new = self.__new_str
                elif self.type == 'b':  # bool
                    self.__new = self.__new_bool
                elif gvar.is_container():  # list
                    self.__new = lambda value, **kwargs: self.__new_list_present(
                        value,
                        **dict([(k, v) for k, v in kwargs.iteritems() if k != 'default'] + [('default', default)])
                    )
                else:
                    self.__new = self.__new_
            elif state == 'absent':
                if self.type == 's':  # bool
                    self.__new = lambda value, **kwargs: self.__new_str(
                        default,
                        **kwargs
                    )
                elif self.type == 'b':  # bool
                    self.__new = lambda value, **kwargs: self.__new_bool(
                        default,
                        **kwargs
                    )
                elif gvar.is_container():  # list
                    self.__new = lambda value, **kwargs: self.__new_list_absent(
                        value,
                        **dict([(k, v) for k, v in kwargs.iteritems() if k != 'default'] + [('default', default)])
                    )
                else:
                    self.__new = lambda value, **kwargs: self.__new(
                        default,
                        **kwargs
                    )
            else:
                raise NotImplementedError('Unknown state')
        else:
            self.__new = self.__new_

if __name__ == '__main__':
    AnsibleGSettingModule().main()
