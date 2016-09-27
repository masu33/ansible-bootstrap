#!/usr/bin/env python
# coding=utf-8
"""
Jinja filter definition for ungrouping a dictionary.
"""

from itertools import chain
from ansible.plugins.filter.core import combine
from ansible.errors import AnsibleFilterError

__author__ = "Sandor Kazi"
__copyright__ = "Copyright 2016, ansible-desktop-bootstrap project"
__credits__ = ["Sandor Kazi"]
__license__ = None
__maintainer__ = "Sandor Kazi"
__email__ = None
__status__ = "Development"


def item2dict(item, default_attribute=None):
    """
    Converts the given item to a dict (if it is not a dict already), using the attribute granted.
    :param item:
    :param default_attribute:
    :return: the original item or a new dict from the supplied default_attribute as key and the item as value
    """
    if isinstance(item, dict):
        return item
    elif default_attribute is None:
        raise AnsibleFilterError('|set an attribute name to use if not all elements are dictionaries')
    else:
        return {default_attribute: item}


def forall(l, default_attribute='name', group_attribute='forall'):
    """
    Ungroup the dictionaries in the iterable l.
    :param l: iterable
    :param default_attribute: name to use as index if the inner item is not a dictionary
    :param group_attribute: name to do the cartesian product for
    :return: the ungrouped iterable
    """
    if l is None:
        return []
    return chain(
        *map(
            lambda item: map(
                lambda inner: combine(item2dict(item, default_attribute), item2dict(inner, default_attribute)),
                item.get(group_attribute, [{}])
            ),
            map(
                lambda item: item2dict(item, default_attribute),
                l
            )
        )
    )


class FilterModule(object):

    @staticmethod
    def filters():
        return {
            'forall': forall,
        }
