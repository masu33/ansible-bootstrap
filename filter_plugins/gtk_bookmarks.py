#!/usr/bin/env python
# coding=utf-8
"""
Jinja filter definition for creating a GTK bookmarks file from a list of items.
"""

from ansible.errors import AnsibleFilterError

__author__ = "Sandor Kazi"
__copyright__ = "Copyright 2016, ansible-desktop-bootstrap project"
__credits__ = ["Sandor Kazi"]
__license__ = None
__maintainer__ = "Sandor Kazi"
__email__ = None
__status__ = "Development"


def __bookmark(item):
    if isinstance(item, dict):
        try:
            if 'name' in item:
                return 'file://{} {}'.format(item['location'], item['name'])
            else:
                return 'file://{}'.format(item['location'])
        except KeyError:
            raise AnsibleFilterError('location must be set in bookmarks')
    elif isinstance(item, (str, unicode)):
        return 'file://{}'.format(item)
    else:
        raise AnsibleFilterError('bookmark definitions can only be dicts or strings')


def gtk_bookmarks(l):
    """
    Creates a GTK bookmark file structure from a list of items
    :param l: list of items to use
    """
    return '\n'.join(map(__bookmark, l))


class FilterModule(object):

    @staticmethod
    def filters():
        return {
            'gtk_bookmarks': gtk_bookmarks,
        }
