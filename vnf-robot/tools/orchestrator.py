import os
from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn

import exc
from DockerController import DockerController, ProcessResult


def deploy(instance, descriptor):
    if instance.suite_source is None:
        raise exc.SetupError('Cannot determine directory of robot file.')

    instance.descriptor_file = descriptor

    instance.docker_controller = DockerController(base_dir=os.path.dirname(instance.suite_source))
    if instance.deployment_options['SKIP_DEPLOY']:
        logger.console('Skipping deployment')
        return ProcessResult(stderr='', stdout='')
    else:
        if instance.descriptor_file is None:
            raise exc.SetupError('No descriptor file specified.')
        logger.console('Deploying {}'.format(instance.descriptor_file))
        return instance.docker_controller.dispatch(
            ['stack', 'deploy', '-c', instance.descriptor_file, instance.deployment_name])


def undeploy(instance):
    instance.docker_controller.dispatch(['stack', 'rm', instance.deployment_name])
    instance.docker_controller = None
