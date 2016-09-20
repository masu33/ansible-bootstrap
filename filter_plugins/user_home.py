from ansible import errors
from subprocess import check_output


def user_home(user):
    result = check_output(
        'grep "^{}:" /etc/passwd | cut -f6 -d:'.format(user),
        shell=True,
    ).strip('\n').strip('\\n')
    if result == "":
        raise errors.AnsibleFilterError('No such user')
    return result


class FilterModule(object):

    @staticmethod
    def filters():
        return {
            'user_home': user_home,
        }
