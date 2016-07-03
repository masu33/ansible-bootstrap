def filter_by_user(seq, user, strict=True):
    try:
        for d in seq:
            users = d.get('users', [])
            if user in users:
                yield d
            elif not strict and not users:
                yield d
    except TypeError:
        pass


class FilterModule(object):

    @staticmethod
    def filters():
        return {
            'filter_by_user': filter_by_user,
        }