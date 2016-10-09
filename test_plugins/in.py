#!/usr/bin/env python
# coding=utf-8
"""
Jinja filter definition for checking inclusion.
"""

from ansible.errors import AnsibleFilterError

__author__ = "Sandor Kazi"
__copyright__ = "Copyright 2016, ansible-desktop-bootstrap project"
__credits__ = ["Sandor Kazi"]
__license__ = None
__maintainer__ = "Sandor Kazi"
__email__ = None
__status__ = "Development"


def in_(*args, **kwargs):
    """
    Checks whether the arguments are a hierarchy.
    :param args: arguments to check
    :param kwargs: keyword arguments to control the process
    :return: whether every one of the arguments are containing the previous/next one
    """
    if len(args) < 2:
        return True
    if any(set(kwargs.keys()) - set('leftwise')):
        raise AnsibleFilterError('valid keyword arguments: leftwise')
    leftwise = kwargs.get('leftwise', False)
    if leftwise:
        return all([v in args[i-1] for i, v in enumerate(args) if i > 0])
    else:
        return all([args[i-1] in v for i, v in enumerate(args) if i > 0])


class TestModule(object):

    def tests(self):
        return {
            'in': in_,
        }
