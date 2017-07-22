#!/usr/bin/env python
# coding=utf-8
"""
Jinja filter definition for table lookups and joins.
"""

from ansible.errors import AnsibleFilterError
from ansible.plugins.filter.core import combine

__author__ = "Sandor Kazi"
__copyright__ = "Copyright 2017, ansible-desktop-bootstrap project"
__credits__ = ["Sandor Kazi"]
__license__ = None
__maintainer__ = "Sandor Kazi"
__email__ = None
__status__ = "Development"


def table_lookup(item, lookup_table, key_name='id'):
    """
    Searches a lookup table and returns the result found (or None).
    :param item: the item to use
    :param lookup_table: the lookup table to search for the key in
    :param key_name: the key to use from the item
    :return: the found item or None
    """
    if key_name in item:
        return lookup_table.get(item[key_name], {})
    else:
        return None


def table_join(item, lookup_table, key_name='id', collection=False):
    """
    Searches a lookup table and merges the dicts.
    :param item: the item to transform
    :param lookup_table: the lookup table to search for the key in
    :param key_name: the key to use from the item
    :param collection: whether to cojoined elements are collections
    :return: the transformed item
    """
    if key_name in item:
        found = table_lookup(item, lookup_table, key_name)
        if collection:
            return [dict(combine(f, item)) for f in found]
        else:
            return dict(combine(found, item))
    else:
        return item


def mass_table_join(items, *args, **kwargs):
    """
    Searches a lookup table and merges the dicts.
    :param items: the items to transform
    :param args: arguments of table_join
    :param kwargs: keyword arguments of table_join
    :return: the transformed items
    """
    return map(lambda x: table_join(x, *args, **kwargs), items)


class FilterModule(object):

    @staticmethod
    def filters():
        return {
            'table_join': table_join,
            'mass_table_join': mass_table_join,
            'table_lookup': table_lookup,
        }
