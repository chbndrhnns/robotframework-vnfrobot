import os
from robot.libraries.BuiltIn import BuiltIn

import namesgenerator
from exc import SetupError, NotFoundError, DeploymentError
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


def deploy(instance, descriptor):
    if instance.suite_source is None:
        raise SetupError('Cannot determine directory of robot file.')

    instance.docker_controller = DockerController(base_dir=os.path.dirname(instance.suite_source))

    # test tool goss: deploy or check the existance
    check_or_create_test_tool_volume(instance.docker_controller, instance.goss_volume)

    instance.descriptor_file = descriptor

    # try to get an existing deployment
    if instance.deployment_name:
        try:
            instance.docker_controller.find_stack(instance.deployment_name)
            BuiltIn().log('Using existing deployment: {}'.format(instance.descriptor_file), level='INFO', console=True)
            return
        except NotFoundError as exc:
            pass

    instance.deployment_name = namesgenerator.get_random_name()

    if instance.descriptor_file is None:
        raise SetupError('No descriptor file specified.')
    try:
        BuiltIn().log('Deploying {}'.format(instance.descriptor_file), level='INFO', console=True)
        instance.docker_controller.deploy_stack(instance.descriptor_file, instance.deployment_name)
    except DeploymentError as exc:
        BuiltIn().log(exc, level='ERROR', console=True)

def undeploy(instance):
    res = instance.docker_controller.undeploy_stack(instance.deployment_name)
    assert len(res.stderr) == 0
    instance.docker_controller = None
    return res
