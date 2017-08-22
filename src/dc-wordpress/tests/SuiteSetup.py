# -*- coding: utf-8 -*-


from robot.api.deco import keyword
from robot.api import logger

from DockerOrchestrator import DockerOrchestrator
import settings
from exc import *
from version import VERSION
from robotlibcore import DynamicCore


class SuiteSetup(DynamicCore):
    """Setup class that creates or reuses an instance of the virtual infrastructure used to perform the tests."""

    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'
    __version__ = VERSION

    orchestrator_mapping = {'docker-compose': DockerOrchestrator}

    def __init__(self):
        DynamicCore.__init__(self, [])

        self.orchestrator = None
        self.orchestrator_type = dict.get(self.orchestrator_mapping, settings.orchestrator)
        logger.info("Importing {}".format(self.__class__))

    def run_keyword(self, name, args, kwargs):
        """
        Mandatory method for using robot dynamic libraries

        Returns:
            None
        """
        logger.info("Running keyword '%s' with arguments %s." % (name, args))
        return self.keywords[name](*args, **kwargs)

    @keyword('Setup test suite')
    def setup(self, project_path=None):
        """
        Setup the virtual infrastructure to run tests on. Supported orchestrators: docker-compose.

        Args:
            project_path: Path where the VNF descriptor resides

        Returns:
            None

        """
        if project_path is None or len(project_path) is 0:
            raise SetupError('Missing parameter: project_path')

        try:
            # noinspection PyCallingNonCallable
            self.orchestrator = self.orchestrator_type()
            self.orchestrator.parse_descriptor(project_path)
            self.orchestrator.create_infrastructure()
        except (DataError, SetupError) as exc:
            raise

