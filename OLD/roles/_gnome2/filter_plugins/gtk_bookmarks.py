#!/usr/bin/env python
# coding=utf-8
"""
Jinja filter definition for creating a GTK bookmarks file from a list of items.
"""

from itertools import chain
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
        if 'state' not in item or item['state'] == 'present':
            try:
                if 'name' in item and item['name']:
                    yield '{}{} {}'.format(
                        item.get('prefix', 'file://').replace(' ', '%20'),
                        item['location'].replace(' ', '%20'),
                        item['name']
                    )
                else:
                    yield '{}{}'.format(
                        item.get('prefix', 'file://').replace(' ', '%20'),
                        item['location'].replace(' ', '%20')
                    )
            except KeyError:
                raise AnsibleFilterError('location must be set in bookmarks')
    elif isinstance(item, (str, unicode)):
        yield item
    else:
        raise AnsibleFilterError('bookmark definitions can only be dicts or location strings')


def gtk_bookmarks(update, current=None):
    """
    Creates a GTK bookmark file structure from a list of items
    :param update: list of items to use
    :param current: original bookmarks
    """
    if current is None:
        current = []
    elif isinstance(current, (str, unicode)):
        current = filter(lambda x: x != '', current.split('\n'))
    else:
        raise AnsibleFilterError('original bookmark definition can only be list or string buffer')

    locations = list(chain(*map(
        lambda x: __bookmark(dict([(k, v) for k, v in x.iteritems() if k in ['prefix', 'location']])),
        update
    )))

    return '\n'.join(
        chain(
            chain(*map(__bookmark, update)),
            filter(lambda item: item.split(' ')[0] not in locations, current)
        )
    )


class FilterModule(object):

    @staticmethod
    def filters():
        return {
            'gtk_bookmarks': gtk_bookmarks,
        }
