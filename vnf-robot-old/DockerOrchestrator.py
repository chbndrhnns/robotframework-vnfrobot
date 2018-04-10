# -*- coding: utf-8 -*-
import socket

import docker
import os
import requests.exceptions
from compose import service
from compose.cli.main import TopLevelCommand, project_from_options
from docker.errors import APIError
from robot.api import logger

from exc import SetupError, ConnectionError, TeardownError, DataError
from interfaces.Orchestrator import Orchestrator


class DockerOrchestrator(Orchestrator):
    default_options = {
        "--no-deps": False,
        "--abort-on-container-exit": False,
        "SERVICE": "",
        "--remove-orphans": False,
        "--no-recreate": True,
        "--force-recreate": False,
        "--build": False,
        '--no-build': False,
        '--no-color': True,
        "--rmi": "none",
        "--volumes": "",
        "--follow": False,
        "--timestamps": True,
        "--tail": "all",
        "-d": True,
        "--scale": "",
        "--host": None,
        "--tlsverify": None,
        "-f": None,
    }

    default_config_options = {
        "--services": False,
        "--volumes": False,
        "--resolve-image-digests": False,
        "--quiet": True,
    }

    default_down_options = {
        "--rmi": None,
        "--volumes": None,
        "--remove-orphans": None,
    }

    def __init__(self):
        super(DockerOrchestrator, self).__init__()

        self.default_options['--host'] = self.settings.docker['DOCKER_HOST']

        self.project = None
        self.project_path = None
        self.volumes = None
        self.networks = None
        self.services = None
        self.commands = None
        self.docker = None

    def deploy(self, project_path=None):
        """
        Setup the virtual infrastructure to run tests on. Supported orchestrators: docker-compose.

        Args:
            project_path: Path where the VNF descriptor resides

        Returns:
            None

        """
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

    def get_instance(self):
        """
        Resolves the docker host and tries to ping it to make sure it is reachable.

        The docker instance can be specified by setting environment variables or modifying the .env file.
        For the variables, see: https://docs.docker.com/machine/reference/env/

        Returns:
            None

        """

        try:
            timeout = float(self.settings.docker['DOCKER_TIMEOUT'])
            self.docker = docker.from_env(environment=self.settings.docker, timeout=timeout)
            self.docker.ping()
        except requests.exceptions.ConnectionError as exc:
            raise ConnectionError(u'{}'.format(exc))

    def parse_descriptor(self, project_path):
        """
        Reads a docker-compose.yml file from the given path.

        Args:
            project_path:

        Returns:
            None

        """
        logger.console(u'Parsing descriptor at "{}"'.format(project_path))

        self.project_path = project_path
        self.project = project_from_options(project_dir=project_path, options=self.default_options)
        self.commands = TopLevelCommand(self.project)

    def validate_descriptor(self):
        """
        Validates a docker-compose descriptor and extracts useful pieces of information:
        - services
        - volumes
        - networks

        Returns:
            None

        """
        if self.project_path is None:
            self.parse_descriptor(self.project_path)

        self.services = [getattr(service, 'name') for service in self.project.services]
        self.volumes = [volume for volume in self.project.volumes.volumes]
        self.networks = [getattr(network, 'name') for network in self.project.networks.networks.values()]

    def create_infrastructure(self):
        try:
            logger.console(u'Creating infrastructure (this can take a while)...')

            return_code = self.commands.up(options=self.default_options)

            if return_code is not 0:
                if return_code is not None:
                    raise SetupError('Could not create infrastructure', return_code)
        except socket.error as exc:
            raise ConnectionError(u'Could not connect to url={}'.format(exc), exc)
        except requests.exceptions.ConnectionError as exc:
            # logger.error(u'{}'.format(exc))
            if u'No such file or directory' in unicode(exc.message):
                raise ConnectionError(u'Could not connect to url={}'.format(exc.request.url), exc)
            elif u'Connection aborted' in unicode(exc.message):
                raise ConnectionError(u'Could not connect to url={}'.format(exc.request.url))

    def destroy_infrastructure(self):
        try:
            logger.console(u'Stopping infrastructure (this can take a while)...', )

            return_code = self.commands.down(self.default_down_options)

            if return_code is not 0:
                if return_code is not None:
                    raise TeardownError('Could not destroy infrastructure', return_code)
        except Exception as exc:
            logger.console(exc)
            raise TeardownError(u'')