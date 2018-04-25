import os

import docker
import mock
from docker import errors
import pytest
from pytest import fixture

from tools import namesgenerator
from modules.context import SUT
from modules.port import Port
from tools import orchestrator
from . import path

from DockerController import DockerController

# import fixtures as local test plugins
pytest_plugins = [
   "tests.fixtures.address",
]

@fixture(scope='module')
def base_name():
    return namesgenerator.get_random_name()


def try_remove_container(controller, name):
    try:
        controller.get_container(name).remove(force=True)
    except (docker.errors.NotFound, docker.errors.APIError) as exc:
        if 'No such container' in exc.explanation:
            pass
        else:
            raise


def try_remove_network(controller, name):
    try:
        controller.get_network(name).remove()
    except (docker.errors.NotFound, docker.errors.APIError) as exc:
        if 'not found' in exc.explanation:
            pass
        else:
            raise


@fixture
def sidecar(base_name, controller, volume):
    data = {
        'name': 'robot_sidecar_for_{}'.format(base_name),
        'controller': controller,
        'volume': volume,
        'image': 'busybox'
    }
    try_remove_container(controller, data.get('name'))
    try_remove_network(controller, data.get('name'))
    yield data
    try_remove_container(controller, data.get('name'))


@fixture
def network(controller, network_name):
    n = None
    try:
        n = controller.get_network(network_name)
    except Exception:
        pass
    finally:
        yield n if n else controller.create_network(network_name)


@fixture(scope='module')
def network_name(stack_infos):
    name = stack_infos[0]
    # return 'robot_sidecar_for_{0}_{1:04d}'.format(name, random.randint(1111,9999))
    return 'robot_sidecar_for_{0}'.format(name)


@fixture(scope='module')
def service_id(stack_infos):
    return '{}_sut'.format(stack_infos[0])


@fixture(scope='module')
def containers(controller, service_id, stack):
    return controller.get_containers_for_service(service_id)


@fixture(scope='module')
def volume(controller, goss_volume_name):
    res = controller.create_volume(goss_volume_name)
    yield goss_volume_name
    controller.delete_volume(goss_volume_name)


@fixture
def gossfile():
    return os.path.join(path, 'fixtures', 'goss-port.yaml')


@fixture
def gossfile_sidecar():
    return os.path.join(path, 'fixtures', 'goss-addr-google.yaml')


@fixture
def container_name(base_name):
    return 'gosstest_{}'.format(base_name)


@fixture(scope='module')
def goss_volume_name(base_name):
    return 'gosstest_{}'.format(base_name)


@fixture(scope='module')
def volume_with_goss(controller, goss_volume_name):
    orchestrator.check_or_create_test_tool_volume(controller, goss_volume_name)
    yield goss_volume_name
    try:
        controller._docker_api.remove_volume(goss_volume_name)
    except errors.APIError:
        pass


@fixture(scope='session')
def controller():
    assert path is not None
    return DockerController(base_dir=path)


@fixture
def container(base_name, controller):
    c = controller.run_busybox()
    yield c
    controller._kill_and_delete_container(c.name)


@fixture
def goss_files():
    return os.path.join(path, 'fixtures', 'goss')


@fixture(scope='module')
def stack_infos(base_name):
    return base_name, os.path.join(path, 'fixtures', 'dc-test.yml')


@fixture(scope='module')
def stack(controller, stack_infos):
    name = stack_infos[0]
    path = stack_infos[1]

    yield (name, path, controller.deploy_stack(path, name))

    controller.undeploy_stack(name)
    try_remove_network(controller, name)
    try_remove_network(controller, 'robot_sidecar_for_{}'.format(name))


# Fixtures for entity tests

@fixture
def application_context():
    return 'application'


@fixture
def service_context():
    return 'service'


@fixture
def node_context():
    return 'node'


@fixture
def network_context():
    return 'network'


@fixture
@pytest.mark.usefixtures('stack_infos')
@pytest.mark.usefixtures('controller')
@mock.patch('LowLevel.BuiltIn', autospec=True)
@mock.patch('LowLevel.LowLevel', autospec=True)
def instance(lib, builtin, stack_infos, controller):
    lib.suite_source = 'bla.robot'
    lib.goss_volume_name = 'goss-helper'
    lib.deployment_name = None
    lib.descriptor_file = stack_infos[1]
    lib.docker_controller = controller
    lib.sut = None
    return lib


# Fixtures for LowLevelEntities

@fixture
def sut():
    return SUT('service', 'sut', 'bla')


@fixture
def port_data():
    return {'context': 'service', 'entity': '6370/TCP', 'property': 'state', 'matcher': 'is', 'value': 'open'}


@fixture
def port(port_data):
    port = Port()
    for k, v in port_data.iteritems():
        port.set(k, v)
    return port


@fixture
@pytest.mark.usefixture('instance')
def port_with_instance(port, instance):
    port.instance = instance
    return port

