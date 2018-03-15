# -*- coding: utf-8 -*-
import collections
from robot.libraries.BuiltIn import BuiltIn

import exc
from robot.api import logger
from robot.api.deco import keyword

from Utils import Utils
from robotlibcore import DynamicCore
from version import VERSION

SUT = collections.namedtuple('sut', 'target_type, target')


class LowLevel(DynamicCore):
    """The Filesystem module contains keywords to validate items on file systems."""

    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'
    __version__ = VERSION

    def __init__(self):
        DynamicCore.__init__(self, [])
        self.context = None
        self.sut = SUT(None, None)

        logger.info(u"Importing {}".format(self.__class__))

    def run_keyword(self, name, args, kwargs):
        """
        Mandatory method for using robot dynamic libraries

        Returns:
            None
        """
        self.context = BuiltIn().get_library_instance(all=True)

        logger.info(u"\nRunning keyword '%s' with arguments %s." % (name, args), also_console=True)
        return self.keywords[name](*args, **kwargs)

    @keyword('Set Target')
    def set_target(self, target_type=None, target=None):
        if target_type is None:
            raise exc.SetupError('No target type given.')
        if target is None:
            raise exc.SetupError('No target given for target_type.')

        self.sut = SUT(target_type, target)

    @keyword('Get Environment Variables')
    def get_env_variables(self):
        allowed_target = ('node',)

        if self.sut.target_type not in allowed_target:
            raise exc.SetupError('Target type "{}" not allowed.'.format(self.sut.target_type))

        return dict([('OS_USERNAME', 'admin'), ('OS_AUTH_URL', 'http://localhost:5000/api')])

    @keyword('Execute Command')
    def execute_command(self):
        allowed_target = ('node',)

        if self.sut.target_type not in allowed_target:
            raise exc.SetupError('Target type "{}" not allowed.'.format(self.sut.target_type))

        return dict([('OS_USERNAME', 'admin'), ('OS_AUTH_URL', 'http://localhost:5000/api')])

    @keyword('Get Process')
    def get_process(self):
        allowed_target = ('node',)

        if self.sut.target_type not in allowed_target:
            raise exc.SetupError('Target type "{}" not allowed.'.format(self.sut.target_type))

        return dict([('OS_USERNAME', 'admin'), ('OS_AUTH_URL', 'http://localhost:5000/api')])

    @keyword('Get Service')
    def get_service(self):
        allowed_target = ('node',)

        if self.sut.target_type not in allowed_target:
            raise exc.SetupError('Target type "{}" not allowed.'.format(self.sut.target_type))

        return dict([('OS_USERNAME', 'admin'), ('OS_AUTH_URL', 'http://localhost:5000/api')])

    @keyword('Get Kernel Parameters')
    def get_kernel_parameter(self):
        allowed_target = ('node',)

        if self.sut.target_type not in allowed_target:
            raise exc.SetupError('Target type "{}" not allowed.'.format(self.sut.target_type))

        return dict([('OS_USERNAME', 'admin'), ('OS_AUTH_URL', 'http://localhost:5000/api')])

    @keyword('Inspect Container')
    def inspect_container(self):
        allowed_target = ('node',)

        if self.sut.target_type not in allowed_target:
            raise exc.SetupError('Target type "{}" not allowed.'.format(self.sut.target_type))

        return dict([('OS_USERNAME', 'admin'), ('OS_AUTH_URL', 'http://localhost:5000/api')])

    @keyword('Check User')
    def check_user(self):
        allowed_target = ('node',)

        if self.sut.target_type not in allowed_target:
            raise exc.SetupError('Target type "{}" not allowed.'.format(self.sut.target_type))

        return dict([('OS_USERNAME', 'admin'), ('OS_AUTH_URL', 'http://localhost:5000/api')])

    @keyword('Check Group')
    def check_group(self):
        allowed_target = ('node',)

        if self.sut.target_type not in allowed_target:
            raise exc.SetupError('Target type "{}" not allowed.'.format(self.sut.target_type))

        return dict([('OS_USERNAME', 'admin'), ('OS_AUTH_URL', 'http://localhost:5000/api')])

    @keyword('Check File')
    def check_file(self):
        allowed_target = ('node',)

        if self.sut.target_type not in allowed_target:
            raise exc.SetupError('Target type "{}" not allowed.'.format(self.sut.target_type))

        return dict([('OS_USERNAME', 'admin'), ('OS_AUTH_URL', 'http://localhost:5000/api')])

    @keyword('Check Symbolic Link')
    def check_symlink(self):
        allowed_target = ('node',)

        if self.sut.target_type not in allowed_target:
            raise exc.SetupError('Target type "{}" not allowed.'.format(self.sut.target_type))

        return dict([('OS_USERNAME', 'admin'), ('OS_AUTH_URL', 'http://localhost:5000/api')])

    @keyword('Check Address')
    def check_address(self):
        allowed_target = ('node',)

        if self.sut.target_type not in allowed_target:
            raise exc.SetupError('Target type "{}" not allowed.'.format(self.sut.target_type))

        return dict([('OS_USERNAME', 'admin'), ('OS_AUTH_URL', 'http://localhost:5000/api')])

    @keyword('Resolve DNS Record')
    def resolve_dns_record(self):
        allowed_target = ('node',)

        if self.sut.target_type not in allowed_target:
            raise exc.SetupError('Target type "{}" not allowed.'.format(self.sut.target_type))

        return dict([('OS_USERNAME', 'admin'), ('OS_AUTH_URL', 'http://localhost:5000/api')])

    @keyword('Check Interface')
    def check_interface(self):
        allowed_target = ('node',)

        if self.sut.target_type not in allowed_target:
            raise exc.SetupError('Target type "{}" not allowed.'.format(self.sut.target_type))

        return dict([('OS_USERNAME', 'admin'), ('OS_AUTH_URL', 'http://localhost:5000/api')])

    @keyword('Check Port')
    def check_port(self):
        allowed_target = ('node',)

        if self.sut.target_type not in allowed_target:
            raise exc.SetupError('Target type "{}" not allowed.'.format(self.sut.target_type))

        return dict([('OS_USERNAME', 'admin'), ('OS_AUTH_URL', 'http://localhost:5000/api')])

