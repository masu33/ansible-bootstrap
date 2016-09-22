def env_check(string):
    return "^" + string.split('=', 1)[0]


class FilterModule(object):

    @staticmethod
    def filters():
        return {
            'env_check': env_check,
        }
