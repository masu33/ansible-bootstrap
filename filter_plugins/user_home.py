#!/usr/bin/env python
# coding=utf-8
"""
Jinja filter definition for getting a user's home folder.
"""

from ansible import errors
from subprocess import check_output

__author__ = "Sandor Kazi"
__copyright__ = "Copyright 2016, ansible-desktop-bootstrap project"
__credits__ = ["Sandor Kazi"]
__license__ = None
__maintainer__ = "Sandor Kazi"
__email__ = None
__status__ = "Development"


def user_home(user):
    """
    Home folder lookup.
    :param user: the user to get the home folder for
    :return: the home folder of the given user
    """
    result = check_output(
        'grep "^{}:" /etc/passwd | cut -f6 -d:'.format(user),
        shell=True,
    ).strip('\n')
    if result == "":
        raise errors.AnsibleFilterError('No such user')
    return result


class FilterModule(object):

    @staticmethod
    def filters():
        return {
            'user_home': user_home,
        }
