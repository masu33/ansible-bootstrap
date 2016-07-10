#!/usr/bin/env python
# coding=utf-8
"""
This module implements an Ansible module to accept the license for the MS TTF EULA.
IMPORTANT NOTE: although the package(s) can be installed this way without accepting the license by hand it does not
exempt anyone from the extent of the license (and it is done through accepting the license automatically).
"""

import subprocess
import json

from ansible.module_utils.basic import AnsibleModule
from ansible.errors import AnsibleOptionsError

__author__ = "Sandor Kazi"
__copyright__ = "Copyright 2016, ansible-desktop-bootstrap project"
__credits__ = ["Sandor Kazi"]
__license__ = "GNU GPL3"
__maintainer__ = "Sandor Kazi"
__email__ = "givenname.familyname_AT_gmail.com"
__status__ = "Development"


class AnsibleMSTTFEULAModule(object):
    """
    Ansible module to accept the license for ttf-mscorefonts-installer package if necessary.
    """

    @classmethod
    def __check_packages(cls, packages):
        # type: (set) -> bool
        """
        Checks which of the packages needs the MS EULA to be accepted.
        :param packages: the packages which will be installed
        :return: the set to
        """
        return 'ttf-mscorefonts-installer' in packages

    @staticmethod
    def __accept_eula():
        # type: () -> str
        """
        Accept the MS EULA to install the package.
        :return: the output of the debconf set
        """
        return subprocess.check_output([
            'echo',
            'ttf-mscorefonts-installer',
            'msttcorefonts/accepted-mscorefonts-eula select true',
            '|',
            'sudo',
            'debconf-set-selections',
        ], shell=True).strip()

    @staticmethod
    def __check_debconf():
        # type: () -> bool
        """
        Check the debconf state for a package.
        :return: whether the debconf for accepting the MS EULA is set.
        """
        check = subprocess.check_output([
            'sudo',
            'debconf-show',
            'ttf-mscorefonts-installer'
        ], shell=False).strip()
        return 'msttcorefonts/accepted-mscorefonts-eula: true' in check

    @classmethod
    def main(cls):
        """
        Executes the given module command.
        """

        # Module specs
        module = AnsibleModule(
            argument_spec={
                'packages': {'required': True},
                'state': {'choices': ['present'], 'default': 'present'},
            },
            supports_check_mode=True,
        )

        # Parameters
        params = module.params
        packages = set(params.get('packages'))
        state = params.get('state')

        # Check parameters
        if state != 'present':
            raise AnsibleOptionsError('The station parameter can only have the value "present"')

        # Check mode
        check_mode = module.check_mode

        # Operation logic
        changed = False
        if cls.__check_packages(packages):
            if not cls.__check_debconf():
                changed = True
                if not check_mode:
                    cls.__accept_eula()

        print json.dumps({
            'changed': changed
        })


if __name__ == '__main__':
    AnsibleMSTTFEULAModule.main()
