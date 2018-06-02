import os
from abc import ABCMeta, abstractmethod

from robot.libraries.BuiltIn import BuiltIn
from ruamel import yaml

from DockerController import DockerController
from exc import SetupError, DeploymentError
from settings import Settings, set_breakpoint
from tools import namesgenerator
from tools.wait_on import wait_on_services_status
from . import path


class Orchestrator:
    __metaclass__ = ABCMeta

    def __init__(self, robot_instance):
        from VnfValidator import VnfValidator
        assert isinstance(robot_instance, VnfValidator), \
            '__init__(): Parameter "robot_instance" needs to be of type VnfValidator'
        self.robot_instance = robot_instance
        self.controller = None

    @abstractmethod
    def get_or_create_deployment(self):
        raise NotImplementedError('Needs implementation.')

    @abstractmethod
    def remove_deployment(self):
        raise NotImplementedError('Needs implementation.')


class DockerOrchestrator(Orchestrator):

    def __init__(self, robot_instance):
        super(DockerOrchestrator, self).__init__(robot_instance)
        self.controller = self._get_controller(self.robot_instance.suite_source) \
            if not self.controller else self.controller

    def get_or_create_test_tool_volume(self, volume):
        try:
            return self.robot_instance.get_volume(volume).name
        except (DeploymentError, AttributeError) as exc:
            if 'not find' in exc:
                return self.check_or_create_test_tool_volume(volume)

    def check_or_create_test_tool_volume(self, volume):
        expected = 'goss-linux-amd64'
        BuiltIn().log('Preparing volume for test tool...', level='INFO', console=Settings.to_console)
        try:
            res = self.controller.list_files_on_volume(volume)
            if expected not in res.stdout:
                raise SetupError('Cannot find {} on volume {}. Please remove the volume to ensure reliable testing.'.
                                 format(expected, volume))
        except DeploymentError:
            BuiltIn().log('Creating volume {}'.format(volume),
                          level='INFO',
                          console=Settings.to_console)
            self.controller.create_volume(volume)
            self.controller.add_data_to_volume(volume, os.path.join(path, 'goss'))
            res = self.controller.list_files_on_volume(volume)

            assert 'goss-linux-amd64' in res.stdout
            assert 'goss-linux-386' in res.stdout
        finally:
            return volume

    @staticmethod
    def _get_controller(source):
        try:
            return DockerController(base_dir=os.path.dirname(source))
        except SetupError as exc:
            raise exc

    def _get_deployment(self, deployment_name=None):
        if self.robot_instance.suite_source is None:
            raise SetupError('\nCannot determine directory of robot file.')

        deployment_name = deployment_name if deployment_name else self.robot_instance.deployment_name

        try:
            self.controller.find_stack(deployment_name)
        except DeploymentError:
            raise SetupError('\nExisting deployment "{}" not found.'.format(deployment_name))

        try:
            # retrieve and store services that belong to the deployment
            self.robot_instance.services.extend(self.controller.get_services(deployment_name))
            assert len(self.robot_instance.services) > 0, \
                "instance.services should not be empty after get_or_create_deployment()"

            # retrieve and store containers that belong to the deployment
            for service in self.robot_instance.services:
                self.robot_instance.containers.extend(self.controller.get_containers_for_service(service.name))
            # set_breakpoint()
            assert len(self.robot_instance.containers) >= len(self.robot_instance.services), \
                "len(instance.containers) should at greater or equal len(self.robot_instance.services) " \
                "after get_deployment()"

            self._health_check_services(self.robot_instance)
            self.robot_instance.deployment_name = deployment_name
        except DeploymentError as exc:
            raise SetupError('\nError during health check: {}'.format(exc.message))

    def _health_check_services(self, instance):
        if not self.robot_instance.services:
            raise SetupError('\n_health_check_services: services list should not be empty')
        wait_on_services_status(self.controller, instance.services)

    def get_or_create_deployment(self):
        try:
            f = os.path.realpath(os.path.join(
                os.path.dirname(self.robot_instance.suite_source),
                self.robot_instance.descriptor_file))
            self.robot_instance.descriptor_file = self._check_file_exists(f)
            self._check_valid_yaml(f)

            deployment_name = self.robot_instance.deployment_name or \
                self.robot_instance.deployment_options.get('USE_DEPLOYMENT')
            if deployment_name:
                self._get_deployment(deployment_name)
            elif len(self.robot_instance.services) is 0:
                self.robot_instance.deployment_name = namesgenerator.get_random_name()
                self._create_deployment()
        except (DeploymentError, SetupError) as exc:
            raise SetupError(exc)

    @staticmethod
    def _check_file_exists(f):
        if not os.path.isfile(f):
            raise SetupError('\nDescriptor "{}" not found.'.format(f))
        return f

    @staticmethod
    def _check_valid_yaml(f):
        try:
            with open(f, 'r') as inp:
                res = yaml.safe_load(inp)
                if not isinstance(res, dict):
                    raise ValueError
        except ValueError:
            raise SetupError('\nDescriptor "{}" is not a valid YAML file.'.format(f))

    def _create_deployment(self):
        descriptor = self.robot_instance.descriptor_file
        deployment_name = self.robot_instance.deployment_name
        ctl = self.controller
        assert deployment_name, "deployment name is required"
        assert descriptor, "descriptor is required"
        assert isinstance(ctl, DockerController), "docker_controller is required"

        try:
            BuiltIn().log('Deploying {} as {}'.format(descriptor, deployment_name), level='INFO',
                          console=True)
            res = self.controller.deploy_stack(descriptor, deployment_name)
            assert res
            self._get_deployment(deployment_name)
        except (DeploymentError, TypeError) as exc:
            raise SetupError('\nError during deployment of {}: \n\t{}'.format(deployment_name, exc))

    def remove_deployment(self):
        if not self.robot_instance.deployment_options['SKIP_UNDEPLOY']:
            if self.robot_instance.services:
                BuiltIn().log('Removing deployment {}...'.format(self.robot_instance.deployment_name), level='INFO',
                              console=True)
                res = self.controller.undeploy_stack(self.robot_instance.deployment_name)
                assert len(res.stderr) == 0
                self.controller = None
                return res
