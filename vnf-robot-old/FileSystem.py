# -*- coding: utf-8 -*-
from robot.libraries.BuiltIn import BuiltIn

import exc
from robot.api import logger, TestSuite, TestData
from robot.api.deco import keyword

from Utils import Utils
from robotlibcore import DynamicCore
from version import VERSION


class FileSystem(DynamicCore):
    """The Filesystem module contains keywords to validate items on file systems."""

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

    @keyword('${node:"?\S+"?} ${operator:has|has no|has not} ${object:file|directory|symlink} ${file:[^\[\S]+}')
    def object_exists(self, node=None, operator='has', object=None, file=None):
        """
        Validates that a file object exists or does not exist on a node.

        Args:
            object: file, directory or symlink
            node: destination node
            operator: has or has not
            file: file path

        Returns:
            None

        """

        Utils.validate_argument(u'node', node)
        Utils.validate_argument(u'operator', operator)
        Utils.validate_argument(u'object', object)
        Utils.validate_string(u'file', file)

    @keyword('${node:"?\S+"?} ${operator:has|has no|has not} ${object:files|directories|symlinks} ${file:\[("\S+",?\s*)+\]}')
    def objects_exist(self, node=None, operator='has', object=None, file=None):
        """
        Validates that file object exist or do not exist on a node.

        Args:
            object: file, directory or symlink
            node: destination node
            operator: has or has not
            files: list of paths to file objects

        Returns:
            None

        """

        Utils.validate_argument(u'node', node)
        Utils.validate_argument(u'operator', operator)
        Utils.validate_argument(u'object', object)
        Utils.validate_list(u'file', file)
