import os
from robot.libraries.BuiltIn import BuiltIn

from tools import namesgenerator
from exc import SetupError, DeploymentError
from DockerController import DockerController
from tools.wait_on import wait_on_services_status

from . import path


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


def deploy(instance, descriptor):
    if instance.suite_source is None:
        raise SetupError('Cannot determine directory of robot file.')

    try:
        if not instance.docker_controller:
            instance.docker_controller = _get_controller(instance.suite_source)
    except SetupError as exc:
        raise exc

    # test tool goss: deploy or check the existance
    instance.test_volume = check_or_create_test_tool_volume(instance.docker_controller, 'goss-helper')

    instance.descriptor_file = descriptor

    # try to get an existing deployment
    if instance.deployment_name:
        try:
            instance.docker_controller.find_stack(instance.deployment_name)
            BuiltIn().log('Using existing deployment: {}'.format(instance.deployment_name), level='INFO', console=True)
            return
        except DeploymentError:
            raise SetupError('Existing deployment {} not found.'.format(instance.deployment_name))

    # create new deployment
    instance.deployment_name = namesgenerator.get_random_name()
    try:
        BuiltIn().log('Deploying {} as {}'.format(instance.descriptor_file, instance.deployment_name), level='INFO', console=True)
        res = instance.docker_controller.deploy_stack(instance.descriptor_file, instance.deployment_name)
        assert res
        BuiltIn().log('Waiting for deployment {}...'.format(instance.deployment_name), level='INFO', console=True)
        instance.services.extend(instance.docker_controller.get_services(instance.deployment_name))
        wait_on_services_status(instance.docker_controller._docker, instance.services)
        return True
    except DeploymentError as exc:
        raise SetupError('Error during deployment of {}: {}'.format(instance.deployment_name, exc))


def undeploy(instance):
    BuiltIn().log('Removing deployment {}...'.format(instance.deployment_name), level='INFO', console=True)
    res = instance.docker_controller.undeploy_stack(instance.deployment_name)
    assert len(res.stderr) == 0
    instance.docker_controller = None
    return res
