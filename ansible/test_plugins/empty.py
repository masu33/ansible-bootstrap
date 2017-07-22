#!/usr/bin/env python
# coding=utf-8
"""
Jinja filter definition for checking emptiness.
"""

from ansible.errors import AnsibleError


def empty(arg):
    """
    Returns whether an iterator or sequence is empty.
    :param arg: iterable
    :return: whether the supplied iterator is empty
    """
    try:
        next(iter(arg))
        return False
    except StopIteration:
        return True
    except TypeError:
        raise AnsibleError('argument not iterable')


class TestModule(object):

    def tests(self):
        return {
            'empty': empty,
        }
