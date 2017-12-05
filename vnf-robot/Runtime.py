# -*- coding: utf-8 -*-
from robot.libraries.BuiltIn import BuiltIn

import exc
from robot.api import logger, TestSuite, TestData
from robot.running import context
from robot.api.deco import keyword

from Utils import Utils
from robotlibcore import DynamicCore
from version import VERSION


class Runtime(DynamicCore):
    """The Runtime module contains keywords to test for runtime configuration."""

    ROBOT_LIBRARY_SCOPE = 'TEST CASE'
    __version__ = VERSION

    def __init__(self):
        DynamicCore.__init__(self, [])
        self.context = None
        self.sut = None

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

    @keyword('On ${host:[^\s,]+}${delim:[,\s]*}${variable:\$\w+} ${operator:is set to|contains} ${value}')
    def environment_with_context(self, host=None, delim=None, *args):
        """
        Validates that an environment variable is set on a specific host.
        The host name is implicitly derived from a setup variable.

        Args:
            delim: optional comma delimiter
            host: the system under test
            variable: an environment variable name
            val: the value of the variable
            operator: the validation operation to perform

        Returns:
            None

        """

        self.environment(*args)

    @keyword('On ${host:[^\s,]+}${delim:[,\s]*}${variable:\$\w+} ${operator:is not set to|contains not|does not contain} ${value}')
    def environment_with_context_negation(self, host=None, delim=None, *args):
        """
        Validates that an environment variable is set on a specific host.
        The host name is implicitly derived from a setup variable.

        Args:
            delim: optional comma delimiter
            host: the system under test
            variable: an environment variable name
            val: the value of the variable
            operator: the validation operation to perform

        Returns:
            None

        """

        self.environment(*args)

    @keyword('${variable:^\$\w+} ${operator:(is set to|contains)} ${value}')
    def environment(self, variable=None, operator=None, val=None):
        """
        Validates that an environment variable is set on a specific host.
        The host name is implicitly derived from a setup variable.

        Args:
            variable: an environment variable name
            val: the value of the variable
            operator: the validation operation to perform

        Returns:
            None

        """

        Utils.validate_argument(u'src', variable)
        Utils.validate_argument(u'operator', operator)
        Utils.validate_argument(u'value', val)

    @keyword('${variable:^\$\w+} ${operator:(is not set to|does not contain|contains not)} ${value}')
    def environment_negation(self, variable=None, operator=None, val=None):
        """
        Validates that an environment variable is not set on a specific host.
        The host name is implicitly derived from a setup variable.

        Args:
            variable: an environment variable name
            val: the value of the variable
            operator: the validation operation to perform

        Returns:
            None

        """

        Utils.validate_argument(u'src', variable)
        Utils.validate_argument(u'operator', operator)
        Utils.validate_argument(u'value', val)

    @keyword('Command ${cmd:".+"} exits with status ${exit_status:([0-9]{1,3\})|("[0-9]{1,3\}")}')
    def command(self, cmd=None, exit_status=None):
        """
        Validates that a command gets executed  on a specific host and verifies the return code is as expected.
        The host name is implicitly derived from a setup variable.

        Args:
            cmd: command that should be executed
            exit_status: return code of the command

        Returns:
            None

        """

        Utils.validate_string(u'cmd', cmd)
        Utils.validate_argument(u'exit_status', exit_status)

    @keyword('Command ${cmd:".+"} exits with status ${exit_status:([0-9]{1,3\})|("[0-9]{1,3\}")} and ${stream:stdout|stderr} contains ${stream_content:".+"}')
    def command_with_stream(self, cmd=None, exit_status=None, stream='stdout', stream_content=None):
        """
        Validates that an environment variable is set on a specific host.
        The host name is implicitly derived from a setup variable.

        Args:
            stream: output stream (stdout or stderr)
            exit_status: return code of the command
            cmd: the command that should be executed
            stream_content: string that is expected in the specified output stream
            operator: the validation operation to perform

        Returns:
            None

        """

        Utils.validate_string(u'cmd', cmd)
        Utils.validate_argument(u'exit_status', exit_status)
        Utils.validate_argument(u'stream', stream)
        Utils.validate_string(u'stream_content', stream_content)

    @keyword('Service ${service:[^\s]+\s|".+"\s}${operator:is|is not} running')
    def service(self, service=None, operator='is'):
        """
        Validates that a service is running on the target machine.
        The host name is implicitly derived from a setup variable.

        Args:
            operator: is or is not
            service: command that should be executed

        Returns:
            None

        """

        Utils.validate_string(u'service', service)
        Utils.validate_string(u'operator', operator)

    def _get_context(self):
        s = TestSuite()
        d = TestData()
        logger.info('')
