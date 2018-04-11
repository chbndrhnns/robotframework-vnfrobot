import mock
from pytest import fixture

from tools.goss import GossTool
from . import path
from DockerController import DockerController
import pytest
from tools.orchestrator import deploy


@fixture
@pytest.mark.usefixtures('stack_infos')
@pytest.mark.usefixtures('controller')
@mock.patch('LowLevel.BuiltIn', autospec=True)
@mock.patch('LowLevel.LowLevel', autospec=True)
def instance(lib, builtin, stack_infos, controller):
    lib.suite_source = 'bla.robot'
    lib.goss_volume = 'goss-helper'
    lib.deployment_name = None
    lib.descriptor_file = stack_infos[1]
    lib.docker_controller = controller
    return lib


@pytest.mark.usefixtures('controller')
def test__run_test_tool__goss__pass(controller, instance, stack_infos, gossfile, containers):
    descriptor = stack_infos[1]
    c = containers[0]

    assert len(containers) > 0

    try:
        deploy(instance, descriptor)
        controller.put_file(c.id, gossfile)
        res = GossTool(controller=controller, target=c, gossfile='/goss-port.yaml').run_goss()

        assert isinstance(res['summary']['failed-count'], int)
    except Exception as exc:
        pytest.fail('No exception should occur. Got: {}'.format(exc))

