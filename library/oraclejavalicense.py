#!/usr/bin/env python
# coding=utf-8
"""
This module implements an Ansible module to accept the license for the Oracle java packages.
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


class AnsibleOracleJavaLicenseModule(object):
    """
    Ansible module to accept the license for oracle java packages if necessary.
    """

    __PACKAGES = {
        'oracle-jdk7-installer',
        'oracle-java7-installer',
        'oracle-java6-installer',
        'oracle-java8-installer',
        'oracle-java9-installer',
    }
    """
    Packages to check for in the package list.
    """

    @classmethod
    def __check_packages(cls, packages):
        # type: (set) -> set
        """
        Checks which of the packages needs the license to be accepted.
        :param packages: the packages which will be installed
        :return: the set that needs the license to be accepted
        """
        return cls.__PACKAGES & packages

    @staticmethod
    def __accept_license(package):
        # type: (str) -> str
        """
        Accept the license to install the package.
        :param package: the package to accept the license for
        :return: the output of the debconf set
        """
        return subprocess.check_output([
            'echo',
            package,
            'shared/accepted-oracle-license-v1-1 select true',
            '|',
            'sudo',
            'debconf-set-selections',
        ], shell=True).strip()

    @staticmethod
    def __check_debconf(package):
        # type: (str) -> bool
        """
        Check the debconf state for a package.
        :param package: the package to check the license for
        :return: whether the debconf for accepting the MS EULA is set.
        """
        check = subprocess.check_output([
            'sudo',
            'debconf-show',
            package
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
        packages_found = cls.__check_packages(packages)
        for p in packages_found:
            if not cls.__check_debconf(p):
                changed = True
                if not check_mode:
                    cls.__accept_license(p)

        print json.dumps({
            'changed': changed,
            'packages': list(packages_found)
        })


if __name__ == '__main__':
    AnsibleOracleJavaLicenseModule.main()
