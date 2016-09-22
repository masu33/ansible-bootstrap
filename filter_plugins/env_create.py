def env_create(d):
    if isinstance(d, str):
        return d
    elif 'line' in d:
        return d['line']
    else:
        return (
            d.get('prefix', '') +
            d.get('name', '') +
            '="' +
            d.get('value_prefix', '').replace('"', '\"') +
            d.get('value', '').replace('"', '\"') +
            d.get('value_postfix', '').replace('"', '\"') +
            '"' +
            d.get('postfix', '')
        )


class FilterModule(object):

    @staticmethod
    def filters():
        return {
            'env_create': env_create,
        }
