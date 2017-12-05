# -*- coding: utf-8 -*-
from robot.libraries.BuiltIn import BuiltIn

import exc
from robot.api import logger, TestSuite, TestData
from robot.api.deco import keyword

from Utils import Utils
from robotlibcore import DynamicCore
from version import VERSION


class Network(DynamicCore):
    """The Network module contains keywords to test for network configuration."""

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

    @keyword('I can reach "${dst}"')
    def network_address_implicit_context(self, dst=None):
        """
        Validates that a destination is reachable from a node and fetches the context from the setup keywords.

        Args:
            dst: the address to test (IPv4, IPv6 or hostname)

        Returns:
            None

        """

        Utils.validate_argument(u'dst', dst)

    @keyword('I cannot reach "${dst}"')
    def network_address_negation_implicit_context(self, dst=None):
        """
        Validates that a destination is not reachable from a node and fetches the context from the setup keywords.

        Args:
            dst: the address to test (IPv4, IPv6 or hostname)

        Returns:
            None

        """

        Utils.validate_argument(u'dst', dst)

    @keyword('From "${src}"${delim:[,\s]*} I can reach "${dst}"')
    def network_address(self, src=None, delim=None, dst=None):
        """
        Validates that a destination is reachable from a node.

        Args:
            src: the node name of the node acting as the source of the test
            delim: used to catch different spelling variants
            dst: the address to test (IPv4, IPv6 or hostname)

        Returns:
            None

        """

        Utils.validate_argument(u'src', src)
        Utils.validate_argument(u'dst', dst)

    @keyword('From ${src}${trash:[,\s]*} I cannot reach ${dst}')
    def network_address_negation(self, src=None, trash=None, dst=None):
        """
        Validate that a destination is not reachable from a node.

        Args:
            src: the node name of the node acting as the source of the test
            dst: the address to test (IPv4, IPv6 or hostname)

        Returns:
            None

        """

        Utils.validate_argument(u'src', src)
        Utils.validate_argument(u'dst', dst)

    # @keyword('${arg:.+}')
    # def network_catch_all(self, arg):
    #     """
    #     Catches any
    #
    #     Args:
    #         arg: any string that cannot be matched against another keyword
    #
    #     Returns:
    #         None
    #
    #     """
    #
    #     raise exc.DataFormatError('Keyword \'{}\' not valid in this context.'.format(arg))

    def _get_context(self):
        s = TestSuite()
        d = TestData()
        logger.info('')
