#!/usr/bin/env python
# coding=utf-8
"""
Jinja filter definition for ungrouping a list of dictionaries.
"""

from itertools import chain
from itertools import product
from ansible.errors import AnsibleFilterError

__author__ = "Sandor Kazi"
__copyright__ = "Copyright 2017, ansible-desktop-bootstrap project"
__credits__ = ["Sandor Kazi"]
__license__ = None
__maintainer__ = "Sandor Kazi"
__email__ = None
__status__ = "Development"


def __remap(item, default_key=None):
    if isinstance(item, dict):
        return item
    elif default_key is None:
        raise AnsibleFilterError('default_key should be set if the input can have non-keyed items')
    else:
        return {default_key: item}


def __product(iterable, default_key=None):
    if isinstance(iterable, dict):
        remapped = map(lambda x: [(x[0], i) for i in x[1]] if isinstance(x[1], list) else [x], iterable.iteritems())
        return map(dict, product(*remapped))
    elif isinstance(iterable, list):
        return map(lambda x: __remap(x, default_key=default_key), iterable)
    else:
        raise AnsibleFilterError('grouping key should contain list or dict')


def forall(l, group_key='forall', default_key=None):
    """
    The following is executed for each item of the list `l`. If the inputs group attribute is a dictionary (supposedly
    key - value-list pairs) it returns all possible combinations of the specialized grouping updating the original
    dictionary keys with it. If it's a list, it considers the combinations to be the elements of the list. Then the
    result is flattened one level.
    :param l: list of dictionaries to use
    :param group_key: name to do the ungrouping for
    :param default_key: name to use for non-iterables to create a dict
    :return: the ungrouped list
    """
    """
    Example:
    [
        {'forall': {'b': [2, 3], 'c': 2}, 'a':1, 'b': 1},
        {'forall': ['f', {}, {'b': 2, 'c': 2}, {'b': 3, 'c': 2}], 'a': 1, 'b': 1},
        {'a': 1, 'b': 1},
    ]
    -->
    [
        {'a': 1, 'b': 2, 'c': 2},       # from the 1st
        {'a': 1, 'b': 3, 'c': 2},       # from the 1st
        {'a': 1, 'b': 1, 'name': 'f'},  # from the 2nd
        {'a': 1, 'b': 1},               # from the 2nd
        {'a': 1, 'b': 2, 'c': 2},       # from the 2nd
        {'a': 1, 'b': 3, 'c': 2},       # from the 2nd
        {'a': 1, 'b': 1},               # from the 3rd
    ]
    """
    l = map(
        lambda x: x if isinstance(x, dict) else {default_key: x},
        l
    )
    return chain(*map(  # flatMap
        lambda list_item: map(
                lambda x: dict(
                    chain(
                        filter(
                            lambda item: item[0] != group_key,
                            list_item.iteritems(),
                        ),
                        x.iteritems()
                    )
                ),
                __product(list_item.get(group_key, [{}]), default_key)
        ),
        l
    ))


def default_key(items, default_key=None):
    """
    Transforms the given list to list of dicts by creating a dict form single elements using the `default_key`
    specified.
    :param items: the list to transform
    :param default_key: the default key to be used
    :return: the transformed list (as a generator)
    """
    return map(lambda x: __remap(x, default_key=default_key), items)


class FilterModule(object):

    @staticmethod
    def filters():
        return {
            'forall': forall,
            'default_key': default_key,
        }
