import os
from robot.libraries.BuiltIn import BuiltIn

import exc
from DockerController import DockerController, ProcessResult

from . import path


def check_or_create_test_tool_volume(instance, volume):
    try:
        res = instance.list_files_on_volume(volume)
        if 'goss-linux-amd64' not in res.stdout:
            raise exc.SetupError
    except exc.SetupError:
        instance.create_volume(volume)
        instance.add_data_to_volume(volume, os.path.join(path, 'goss'))
        res = instance.list_files_on_volume(volume)

        assert 'goss-linux-amd64' in res.stdout
        assert 'goss-linux-386' in res.stdout


def deploy(instance, descriptor):
    if instance.suite_source is None:
        raise exc.SetupError('Cannot determine directory of robot file.')

    instance.docker_controller = DockerController(base_dir=os.path.dirname(instance.suite_source))

    # test tool goss: deploy or check the existance
    check_or_create_test_tool_volume(instance.docker_controller, instance.goss_volume)

    instance.descriptor_file = descriptor

    if instance.deployment_options['SKIP_DEPLOY']:
        BuiltIn().log('Skipping deployment', level="INFO", console=True)
        return ProcessResult(stderr='', stdout='')
    else:
        if instance.descriptor_file is None:
            raise exc.SetupError('No descriptor file specified.')
        BuiltIn().log('Deploying {}'.format(instance.descriptor_file), level='INFO', console=True)
        return instance.docker_controller.stack_deploy(instance.descriptor_file, instance.deployment_name)


def undeploy(instance):
    res = instance.docker_controller.stack_undeploy(instance.deployment_name)
    assert len(res.stderr) == 0
    instance.docker_controller = None
    return res
