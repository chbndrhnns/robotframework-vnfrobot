# -*- coding: utf-8 -*-
import os

import compose.config
from compose import service
from docker.errors import APIError
from robot.api import logger
from robot.api.deco import keyword

from DockerOrchestrator import DockerOrchestrator
from exc import ConnectionError, SetupError, DataError, TeardownError
from interfaces.Orchestrator import Orchestrator
from robotlibcore import DynamicCore
from version import VERSION


class SuiteTools(DynamicCore):
    """Setup class that creates or reuses an instance of the virtual infrastructure used to perform the tests."""

    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'
    __version__ = VERSION

    orchestrator_mapping = {'docker-compose': DockerOrchestrator}

    def __init__(self):
        DynamicCore.__init__(self, [])

        self.orchestrator = None
        self.project_path = None
        self.orchestrator_type = dict.get(self.orchestrator_mapping, self.settings.orchestrator)
        logger.info(u"Importing {}".format(self.__class__))

    def run_keyword(self, name, args, kwargs):
        """
        Mandatory method for using robot dynamic libraries

        Returns:
            None
        """
        logger.info(u"Running keyword '%s' with arguments %s." % (name, args))
        return self.keywords[name](*args, **kwargs)

    def deploy(self, project_path=None):
        """
        Setup the virtual infrastructure to run tests on. Supported orchestrators: docker-compose.

        Args:
            project_path: Path where the VNF descriptor resides

        Returns:
            None

        """
        # TODO: extract docker-compose-specific checks into DockerOrchestrator
        logger.debug(u'Checking for arguments: "{}"'.format('project_path'))
        if project_path is None or len(project_path) is 0:
            raise SetupError(u'Missing parameter: project_path')

        project_file = 'docker-compose.yml'
        logger.debug(u'Looking for {}'.format(project_file))
        if not os.path.isfile(os.path.join(project_path, project_file)):
            if not os.path.isfile(os.path.join(project_path, 'docker-compose.yaml')):
                raise SetupError(u'No docker-compose file found in "{}"'.format(project_path))
            else:
                project_file = 'docker-compose.yaml'

        logger.debug(u'Looking for Dockerfile')
        if not os.path.isfile(os.path.join(project_path, 'Dockerfile')):
            raise SetupError(u'No Dockerfile found in "{}"'.format(project_path))

        if os.path.getsize(os.path.join(project_path, project_file)) is 0:
            raise SetupError(u'docker-compose file must not be empty')
        if os.path.getsize(os.path.join(project_path, 'Dockerfile')) is 0:
            raise SetupError(u'Dockerfile must not be empty')

        self.project_path = project_path

        try:
            logger.debug(u'Using orchestrator type "{}"'.format(self.orchestrator_type))
            # noinspection PyCallingNonCallable
            self.orchestrator = self.orchestrator_type()
            self.orchestrator.parse_descriptor(project_path)
            self.orchestrator.create_infrastructure()
        except service.BuildError as exc:
            logger.error(u'Build error: {}'.format(exc.reason))
            raise SetupError(exc)
        except compose.config.ConfigurationError as exc:
            logger.error(u'Parse error: {}'.format(exc.msg))
            raise SetupError(exc)
        except ConnectionError as exc:
            # logger.error(u'Connection error: {}\n\n{}'.format(exc.message, exc.args[1]))
            raise exc
        except APIError as exc:
            logger.error(u'Error: {}\n\n{}'.format(exc.message, exc.explanation))
            raise exc
        except (DataError, SetupError) as exc:
            logger.error(u'Connection error: {}\n\n{}'.format(exc.message, exc.args[1]))
            raise exc

    @keyword('Teardown test suite')
    def teardown(self, level='destroy'):
        """
        After a test session run is completed, the virtual infrastructure needs to be either
        - stopped (can be restarted quickly),
        - cleaned (base images are kept, custom configuration is removed) or
        - destroyed (base images and custom configuration is removed).

        Args:
            level (str): level of teardown, one of TearDownLevel

        Returns:
            None

        """
        # import pydevd
        # pydevd.settrace('localhost', port=65000, stdoutToServer=True, stderrToServer=True)

        if level not in Orchestrator.teardown_levels:
            raise TeardownError(u'Teardown "{}" level not in {}'.format(level, Orchestrator.teardown_levels))

        logger.debug(u'Tearing down with level "{}"'.format(level))

        if self.orchestrator is None:
            raise TeardownError(u'No orchestrator found.')

        try:
            self.orchestrator.destroy_infrastructure()
        except TeardownError as exc:
            logger.error(u'Teardown Error: {}'.format(exc))





