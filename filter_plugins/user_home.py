#!/usr/bin/env python
# coding=utf-8
"""
Jinja filter definition for checking user details.
"""

import pwd
from ansible.errors import AnsibleFilterError

__author__ = "Sandor Kazi"
__copyright__ = "Copyright 2016, ansible-desktop-bootstrap project"
__credits__ = ["Sandor Kazi"]
__license__ = None
__maintainer__ = "Sandor Kazi"
__email__ = None
__status__ = "Development"


def user_attribute(user, key):
    """
    User attribute lookup.
    :param user: the user to get the attribute for
    :param key: the attribute index to return
    :return: the attribute of the given user
    """
    try:
        return pwd.getpwnam(user).__getattribute__(key)
    except KeyError:
        raise AnsibleFilterError('No such user {}'.format(user))
    except AttributeError:
        raise AnsibleFilterError('Wrong index supplied: {}'.format(key))


class FilterModule(object):

    @staticmethod
    def filters():
        return {
            'user_home': lambda x: user_attribute(x, 'pw_dir'),
        }
