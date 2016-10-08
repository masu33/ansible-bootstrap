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


def user_exists(user):
    """
    Check user existence.
    :param user: the user to check
    :return: boolean whether the given user exists
    """
    try:
        with open(__passwd) as fin:
            for _ in filter(lambda x: x.startswith('{}:'.format(user)), fin):
                return True
            else:
                return False
    except IOError:
        raise AnsibleFilterError('Environment problem: could not run read {}'.format(__passwd))


class TestModule(object):

    def tests(self):
        return {
            'user_exists': user_exists,
        }
