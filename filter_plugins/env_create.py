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
            str.replace(d.get('value_prefix', ''), '"', '\"') +
            str.replace(d.get('value', ''), '"', '\"') +
            str.replace(d.get('value_postfix', ''), '"', '\"') +
            '"' +
            d.get('postfix', '')
        )


class FilterModule(object):

    @staticmethod
    def filters():
        return {
            'env_create': env_create,
        }
