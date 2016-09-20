from itertools import chain
from ansible.compat.six import iteritems, string_types

from ansible import errors
from ansible.utils.vars import merge_hash


def combine_left(*terms, **kwargs):
    recursive = kwargs.get('recursive', False)
    if len(kwargs) > 1 or (len(kwargs) == 1 and 'recursive' not in kwargs):
        raise errors.AnsibleFilterError("'recursive' is the only valid keyword argument")

    for t in terms:
        if not isinstance(t, dict):
            raise errors.AnsibleFilterError("|combine_left expects dictionaries, got " + repr(t))

    if recursive:
        return reduce(merge_hash, terms[::-1])
    else:
        return dict(chain(*map(iteritems, terms[::-1])))


class FilterModule(object):

    @staticmethod
    def filters():
        return {
            'combine_left': combine_left,
        }
