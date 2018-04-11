import os
from robot.libraries.BuiltIn import BuiltIn

import namesgenerator
from exc import SetupError, DeploymentError
from DockerController import DockerController

from . import path


def check_or_create_test_tool_volume(instance, volume):
    try:
        res = instance.list_files_on_volume(volume)
        if 'goss-linux-amd64' not in res.stdout:
            raise SetupError
    except SetupError:
        instance.create_volume(volume)
        instance.add_data_to_volume(volume, os.path.join(path, 'goss'))
        res = instance.list_files_on_volume(volume)

        assert 'goss-linux-amd64' in res.stdout
        assert 'goss-linux-386' in res.stdout


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
    check_or_create_test_tool_volume(instance.docker_controller, instance.goss_volume)

    instance.descriptor_file = descriptor

    # try to get an existing deployment
    if instance.deployment_name:
        if instance.docker_controller.find_stack(instance.deployment_name):
            BuiltIn().log('Using existing deployment: {}'.format(instance.deployment_name), level='INFO', console=True)
            return
        else:
            raise SetupError('Existing deployment {} not found.'.format(instance.deployment_name))

    # create new deployment
    instance.deployment_name = namesgenerator.get_random_name()
    try:
        BuiltIn().log('Deploying {}'.format(instance.descriptor_file), level='INFO', console=True)
        instance.docker_controller.deploy_stack(instance.descriptor_file, instance.deployment_name)
        return True
    except DeploymentError as exc:
        raise SetupError('Error during deployment: {}'.format(exc))


def undeploy(instance):
    res = instance.docker_controller.undeploy_stack(instance.deployment_name)
    assert len(res.stderr) == 0
    instance.docker_controller = None
    return res
