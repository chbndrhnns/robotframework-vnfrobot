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

    @keyword('Environment Variable')
    def env_variable(self):
        allowed_target = ('node',)

        if self.sut.target_type not in allowed_target:
            raise exc.SetupError('Target type "{}" not allowed.'.format(self.sut.target_type))

        return dict([('OS_USERNAME', 'admin'), ('OS_AUTH_URL', 'http://localhost:5000/api')])

    @keyword('Command')
    def command(self):
        allowed_target = ('node',)

        if self.sut.target_type not in allowed_target:
            raise exc.SetupError('Target type "{}" not allowed.'.format(self.sut.target_type))

        return dict([('OS_USERNAME', 'admin'), ('OS_AUTH_URL', 'http://localhost:5000/api')])

    @keyword('Process')
    def process(self):
        allowed_target = ('node',)

        if self.sut.target_type not in allowed_target:
            raise exc.SetupError('Target type "{}" not allowed.'.format(self.sut.target_type))

        return dict([('OS_USERNAME', 'admin'), ('OS_AUTH_URL', 'http://localhost:5000/api')])

    @keyword('Service')
    def service(self):
        allowed_target = ('node',)

        if self.sut.target_type not in allowed_target:
            raise exc.SetupError('Target type "{}" not allowed.'.format(self.sut.target_type))

        return dict([('OS_USERNAME', 'admin'), ('OS_AUTH_URL', 'http://localhost:5000/api')])

    @keyword('Kernel Parameter')
    def kernel_parameter(self):
        allowed_target = ('node',)

        if self.sut.target_type not in allowed_target:
            raise exc.SetupError('Target type "{}" not allowed.'.format(self.sut.target_type))

        return dict([('OS_USERNAME', 'admin'), ('OS_AUTH_URL', 'http://localhost:5000/api')])

    @keyword('Container')
    def container(self):
        allowed_target = ('node',)

        if self.sut.target_type not in allowed_target:
            raise exc.SetupError('Target type "{}" not allowed.'.format(self.sut.target_type))

        return dict([('OS_USERNAME', 'admin'), ('OS_AUTH_URL', 'http://localhost:5000/api')])

    @keyword('User')
    def user(self):
        allowed_target = ('node',)

        if self.sut.target_type not in allowed_target:
            raise exc.SetupError('Target type "{}" not allowed.'.format(self.sut.target_type))

        return dict([('OS_USERNAME', 'admin'), ('OS_AUTH_URL', 'http://localhost:5000/api')])

    @keyword('Group')
    def group(self):
        allowed_target = ('node',)

        if self.sut.target_type not in allowed_target:
            raise exc.SetupError('Target type "{}" not allowed.'.format(self.sut.target_type))

        return dict([('OS_USERNAME', 'admin'), ('OS_AUTH_URL', 'http://localhost:5000/api')])

    @keyword('File')
    def file(self):
        allowed_target = ('node',)

        if self.sut.target_type not in allowed_target:
            raise exc.SetupError('Target type "{}" not allowed.'.format(self.sut.target_type))

        return dict([('OS_USERNAME', 'admin'), ('OS_AUTH_URL', 'http://localhost:5000/api')])

    @keyword('Symbolic Link')
    def symlink(self):
        allowed_target = ('node',)

        if self.sut.target_type not in allowed_target:
            raise exc.SetupError('Target type "{}" not allowed.'.format(self.sut.target_type))

        return dict([('OS_USERNAME', 'admin'), ('OS_AUTH_URL', 'http://localhost:5000/api')])

    @keyword('Address')
    def address(self):
        allowed_target = ('node',)

        if self.sut.target_type not in allowed_target:
            raise exc.SetupError('Target type "{}" not allowed.'.format(self.sut.target_type))

        return dict([('OS_USERNAME', 'admin'), ('OS_AUTH_URL', 'http://localhost:5000/api')])

    @keyword('DNS')
    def dns(self):
        allowed_target = ('node',)

        if self.sut.target_type not in allowed_target:
            raise exc.SetupError('Target type "{}" not allowed.'.format(self.sut.target_type))

        return dict([('OS_USERNAME', 'admin'), ('OS_AUTH_URL', 'http://localhost:5000/api')])

    @keyword('Interface')
    def interface(self):
        allowed_target = ('node',)

        if self.sut.target_type not in allowed_target:
            raise exc.SetupError('Target type "{}" not allowed.'.format(self.sut.target_type))

        return dict([('OS_USERNAME', 'admin'), ('OS_AUTH_URL', 'http://localhost:5000/api')])

    @keyword('Port')
    def port(self):
        allowed_target = ('node',)

        if self.sut.target_type not in allowed_target:
            raise exc.SetupError('Target type "{}" not allowed.'.format(self.sut.target_type))

        return dict([('OS_USERNAME', 'admin'), ('OS_AUTH_URL', 'http://localhost:5000/api')])

