#!/usr/bin/env python
# coding=utf-8
"""
Jinja filter definition for checking user details in /etc/passwd.
"""

from ansible.errors import AnsibleFilterError

__author__ = "Sandor Kazi"
__copyright__ = "Copyright 2016, ansible-desktop-bootstrap project"
__credits__ = ["Sandor Kazi"]
__license__ = None
__maintainer__ = "Sandor Kazi"
__email__ = None
__status__ = "Development"

__passwd = '/etc/passwd'


def user_attribute(user, num):
    """
    User attribute lookup.
    :param user: the user to get the attribute for
    :param num: the attribute index to return
    :return: the attribute of the
    """
    try:
        with open(__passwd) as fin:
            for line in filter(lambda x: x.startswith('{}:'.format(user)), fin):
                try:
                    return line.split(':', num+1)[num]
                except IndexError:
                    raise AnsibleFilterError('Wrong index supplied: {}'.format(num))
            else:
                raise AnsibleFilterError('No such user {}'.format(user))
    except IOError:
        raise AnsibleFilterError('Environment problem: could not run read {}'.format(__passwd))


class FilterModule(object):

    @staticmethod
    def filters():
        return {
            'user_home': lambda x: user_attribute(x, 5),
        }
