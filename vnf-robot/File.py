# -*- coding: utf-8 -*-
import os

from robot.api import logger
from robot.api.deco import keyword

from exc import ConnectionError
from interfaces.Orchestrator import Orchestrator
from robotlibcore import DynamicCore
from settings import Settings
from version import VERSION


class File(DynamicCore):
    """Command is used to validate the state of a file."""

    ROBOT_LIBRARY_SCOPE = 'TEST CASE'
    __version__ = VERSION

    def __init__(self):
        DynamicCore.__init__(self, [])

        logger.info("Importing {}".format(self.__class__))
        self.settings = Settings()

    def run_keyword(self, name, args, kwargs):
        """
        Mandatory method for using robot dynamic libraries

        Returns:
            None
        """
        logger.info("Running keyword '%s' with arguments %s." % (name, args))
        return self.keywords[name](*args, **kwargs)

    @keyword('File ${file} exists')
    def file_exists(self, file):
        """
        Checks whether a file exists.

        Returns:

        """

        # get orchestrator instance

        #
