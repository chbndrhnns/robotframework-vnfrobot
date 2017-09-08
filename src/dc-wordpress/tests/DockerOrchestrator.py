# -*- coding: utf-8 -*-
import docker
from robot.api import logger

import requests.exceptions
from compose.cli.main import TopLevelCommand, project_from_options

from Orchestrator import Orchestrator
from exc import SetupError, ConnectionError, TeardownError


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
        '--no-color': False,
        "--rmi": "none",
        "--volumes": "",
        "--follow": False,
        "--timestamps": True,
        "--tail": "all",
        "-d": True,
        "--scale": "",
        "--host": None,
        "--tlsverify": None
    }

    default_config_options = {
        "--services": False,
        "--volumes": False,
        "--resolve-image-digests": False,
        "--quiet": True}

    default_down_options = {
        "--rmi": None,
        "--volumes": None,
        "--remove-orphans": None
    }

    def __init__(self):
        super(DockerOrchestrator, self).__init__()

        self.default_options['--host'] = self.settings.docker['DOCKER_HOST']

        self.project = None
        self.volumes = None
        self.networks = None
        self.services = None
        self.commands = None
        self.docker = None

    def get_instance(self):
        """
        Resolves the docker host and tries to ping it to make sure it is reachable.

        The docker instance can be specified by setting environment variables or modifying the .env file.
        For the variables, see: https://docs.docker.com/machine/reference/env/

        Returns:
            None

        """
        self.docker = docker.from_env(environment=self.settings.docker)
        self.docker.ping()

    def parse_descriptor(self, project_path):
        """
        Reads a docker-compose.yml file from the given path.

        Args:
            project_path:

        Returns:
            None

        """
        logger.console(u'Parsing descriptor at "{}"'.format(project_path))

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
        self.commands.config(config_options=self.default_options, options=self.default_config_options)

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
        except requests.exceptions.ConnectionError as exc:
            logger.error(u'{}'.format(exc))
            if 'No such file or directory' in str(exc.message):
                raise ConnectionError(u'Could not connect to url={}'.format(exc.request.url), exc)
            else:
                raise ConnectionError(u'Not specified connection error.')

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