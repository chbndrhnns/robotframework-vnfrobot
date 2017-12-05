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


    def _get_context(self):
        s = TestSuite()
        d = TestData()
        logger.info('')
