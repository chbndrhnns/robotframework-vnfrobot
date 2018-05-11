import os

from robot.libraries.BuiltIn import BuiltIn
from ruamel import yaml

from DockerController import DockerController
from exc import SetupError, DeploymentError
from settings import Settings
from tools import namesgenerator
from tools.testutils import set_breakpoint
from tools.wait_on import wait_on_services_status
from . import path


def get_or_create_test_tool_volume(instance, volume):
    try:
        return instance.get_volume(volume).name
    except (DeploymentError, AttributeError) as exc:
        if 'not find' in exc:
            return check_or_create_test_tool_volume(instance, volume)


def check_or_create_test_tool_volume(instance, volume):
    expected = 'goss-linux-amd64'
    BuiltIn().log('Preparing volume for test tool...', level='INFO', console=Settings.to_console)
    try:
        res = instance.list_files_on_volume(volume)
        if expected not in res.stdout:
            raise SetupError('Cannot find {} on volume {}'.format(expected, volume))
    except DeploymentError:
        BuiltIn().log('Creating volume {}'.format(volume),
                      level='INFO',
                      console=Settings.to_console)
        instance.create_volume(volume)
        instance.add_data_to_volume(volume, os.path.join(path, 'goss'))
        res = instance.list_files_on_volume(volume)

        assert 'goss-linux-amd64' in res.stdout
        assert 'goss-linux-386' in res.stdout
    finally:
        return volume


def _get_controller(source):
    try:
        return DockerController(base_dir=os.path.dirname(source))
    except SetupError as exc:
        raise exc


def _get_deployment(instance):
    if instance.suite_source is None:
        raise SetupError('Cannot determine directory of robot file.')

    try:
        instance.docker_controller.find_stack(instance.deployment_name)
        if not instance.services:
            BuiltIn().log('Using existing deployment: {}'.format(instance.deployment_name), level='INFO',
                          console=Settings.to_console)

        # retrieve and store services that belong to the deployment
        instance.services.extend(instance.docker_controller.get_services(instance.deployment_name))
        assert len(instance.services) > 0, \
            "instance.services should not be empty after get_or_create_deployment()"

        # retrieve and store containers that belong to the deployment
        for service in instance.services:
            instance.containers.extend(instance.docker_controller.get_containers_for_service(service.name))
        # set_breakpoint()
        assert len(instance.containers) >= len(instance.services), \
            "instance.containers should not be empty after get_or_create_deployment()"
    except DeploymentError:
        raise SetupError('Existing deployment {} not found.'.format(instance.deployment_name))

    try:
        _health_check_services(instance)
        return True
    except DeploymentError as exc:
        raise SetupError('Error during health check: {}'.format(exc.message))


def _health_check_services(instance):
    assert instance.services, '_health_check_services: services list should not be empty'
    wait_on_services_status(instance.docker_controller, instance.services)


def get_or_create_deployment(instance):
    try:
        f = os.path.realpath(os.path.join(os.path.dirname(instance.suite_source), instance.descriptor_file))
        instance.descriptor_file = _check_file_exists(f)
        _check_valid_yaml(f)
        if not instance.docker_controller:
            instance.docker_controller = _get_controller(instance.suite_source)
        if instance.deployment_name:
            _get_deployment(instance)
        elif len(instance.services) is 0:
            instance.deployment_name = namesgenerator.get_random_name()
            _create_deployment(instance)
    except (DeploymentError, SetupError) as exc:
        raise SetupError(exc)


def _check_file_exists(f):
    if not os.path.isfile(f):
        raise SetupError('Descriptor "{}" not found.'.format(f))
    return f


def _check_valid_yaml(f):
    try:
        with open(f, 'r') as inp:
            res = yaml.safe_load(inp)
            if not isinstance(res, dict):
                raise ValueError
    except ValueError:
        raise SetupError('Descriptor "{}" is not a valid YAML file.'.format(f))


def _create_deployment(instance):
    descriptor = instance.descriptor_file
    deployment = instance.deployment_name
    ctl = instance.docker_controller
    assert deployment, "deployment name is required"
    assert descriptor, "descriptor is required"
    assert ctl, "docker_controller is required"

    try:
        BuiltIn().log('Deploying {} as {}'.format(descriptor, deployment), level='INFO',
                      console=True)
        res = instance.docker_controller.deploy_stack(descriptor, deployment)
        assert res
        _get_deployment(instance)
    except (DeploymentError, TypeError) as exc:
        raise SetupError('Error during deployment of {}: {}'.format(deployment, exc))


def remove_deployment(instance):
    if not instance.deployment_options['SKIP_UNDEPLOY']:
        if instance.services:
            BuiltIn().log('Removing deployment {}...'.format(instance.deployment_name), level='INFO',
                          console=True)
            res = instance.docker_controller.undeploy_stack(instance.deployment_name)
            assert len(res.stderr) == 0
            instance.docker_controller = None
            return res
