import os

from docker.errors import NotFound
from robot.libraries.BuiltIn import BuiltIn

from tools import namesgenerator
from exc import SetupError, DeploymentError
from DockerController import DockerController
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
    BuiltIn().log('Preparing volume for test tool...', level='INFO', console=True)
    try:
        res = instance.list_files_on_volume(volume)
        if expected not in res.stdout:
            raise SetupError('Cannot find {} on volume {}'.format(expected, volume))
    except DeploymentError:
        BuiltIn().log_to_console('Creating volume {}'.format(volume))
        instance.create_volume(volume)
        instance.add_data_to_volume(volume, os.path.join(path, 'goss'))
        res = instance.list_files_on_volume(volume)

        assert 'goss-linux-amd64' in res.stdout
        assert 'goss-linux-386' in res.stdout
    finally:
        return volume


def _get_controller(source):
    return DockerController(base_dir=os.path.dirname(source))


def _get_deployment(instance):
    if instance.suite_source is None:
        raise SetupError('Cannot determine directory of robot file.')

    try:
        if not instance.docker_controller:
            instance.docker_controller = _get_controller(instance.suite_source)
    except SetupError as exc:
        raise exc

    if instance.deployment_name:
        try:
            instance.docker_controller.find_stack(instance.deployment_name)
            if not instance.services:
                BuiltIn().log('Using existing deployment: {}'.format(instance.deployment_name), level='INFO',
                              console=True)
        except DeploymentError:
            raise SetupError('Existing deployment {} not found.'.format(instance.deployment_name))
    else:
        instance.deployment_name = namesgenerator.get_random_name()
        # BuiltIn().log('Name for the deployment: {}'.format(instance.deployment_name), level='DEBUG', console=True)
    return True


def get_or_create_deployment(instance):
    try:
        f = os.path.realpath(os.path.join(os.path.dirname(instance.suite_source), instance.descriptor_file))
        instance.descriptor_file = _check_file_exists(f)
        if instance.deployment_name:
            _get_deployment(instance)
        elif len(instance.services) is 0:
            _create_deployment(instance)
    except (DeploymentError, SetupError) as exc:
        raise exc


def _check_file_exists(f):
    if not os.path.isfile(f):
        raise SetupError('Descriptor "{}" not found.'.format(f))
    return f



def _create_deployment(instance):
    descriptor = instance.descriptor_file
    deployment = instance.deployment_name
    ctl = instance.docker_controller
    assert deployment
    assert descriptor
    assert ctl

    try:
        BuiltIn().log('Deploying {} as {}'.format(descriptor, deployment), level='INFO',
                      console=True)
        res = instance.docker_controller.deploy_stack(descriptor, deployment)
        assert res
        BuiltIn().log('Waiting for deployment {}...'.format(deployment), level='INFO', console=True)
        instance.services.extend(ctl.get_services(deployment))
        wait_on_services_status(ctl._docker, instance.services)
        return True
    except DeploymentError as exc:
        raise SetupError('Error during deployment of {}: {}'.format(deployment, exc))


def remove_deployment(instance):
    if instance.services:
        BuiltIn().log('Removing deployment {}...'.format(instance.deployment_name), level='INFO', console=True)
        res = instance.docker_controller.undeploy_stack(instance.deployment_name)
        assert len(res.stderr) == 0
        instance.docker_controller = None
        return res
