# -*- coding: utf-8 -*-
import compose.config
import os

from compose import service
from docker.errors import APIError
from robot.api.deco import keyword
from robot.api import logger

from DockerOrchestrator import DockerOrchestrator
import settings
from exc import ConnectionError, SetupError, DataError
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
        # TODO: extract docker-compose-specific checks into DockerOrchestrator
        if project_path is None or len(project_path) is 0:
            raise SetupError(u'Missing parameter: project_path')

        project_file = 'docker-compose.yml'
        if not os.path.isfile(os.path.join(project_path, project_file)):
            if not os.path.isfile(os.path.join(project_path, 'docker-compose.yaml')):
                raise SetupError(u'No docker-compose file found in "{}"'.format(project_path))
            else:
                project_file = 'docker-compose.yaml'

        if not os.path.isfile(os.path.join(project_path, 'Dockerfile')):
            raise SetupError(u'No Dockerfile found in "{}"'.format(project_path))

        if os.path.getsize(os.path.join(project_path, project_file)) is 0:
            raise SetupError(u'docker-compose file must not be empty')
        if os.path.getsize(os.path.join(project_path, 'Dockerfile')) is 0:
            raise SetupError(u'Dockerfile must not be empty')

        try:
            # noinspection PyCallingNonCallable
            logger.debug(u'Using orchestrator type "{}"'.format(self.orchestrator_type))
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
            logger.error(u'Connection error: {}\n\n{}'.format(exc.message, exc.args[1]))
            raise exc
        except APIError as exc:
            logger.error(u'Error: {}\n\n{}'.format(exc.message, exc.explanation))
            raise exc
        except (DataError, SetupError) as exc:
            logger.error(u'Connection error: {}\n\n{}'.format(exc.message, exc.args[1]))
            raise exc

