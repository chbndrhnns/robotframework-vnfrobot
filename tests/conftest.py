from __future__ import absolute_import
import os

from docker import errors
import pytest
from docker.models.resource import Collection
from docker.models.services import Service
from pytest import fixture

import VnfValidator
from exc import NotFoundError
from testtools.DockerTool import DockerTool
from testtools.GossTool import GossTool
from tools import namesgenerator
from tools.data_structures import SUT
from tools import orchestrator
from tools.orchestrator import DockerOrchestrator
from tools.wait_on import wait_on_services_status
from . import path

from DockerController import DockerController

# import fixtures as local test plugins
pytest_plugins = [
    "tests.fixtures.context",
    "tests.fixtures.command",
    "tests.fixtures.address",
    "tests.fixtures.file",
    "tests.fixtures.port",
    "tests.fixtures.goss",
    "tests.fixtures.placement",
]


@fixture(scope='module')
def base_name():
    return namesgenerator.get_random_name()


def try_remove_container(controller, name):
    try:
        controller.get_container(name).remove(force=True)
    except NotFoundError as exc:
        pass


def try_remove_network(controller, name):
    try:
        controller.get_network(name).remove()
    except NotFoundError as exc:
        pass


@fixture(scope='module')
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
    yield controller.get_or_create_network(network_name)


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
    try:
        controller.delete_volume(goss_volume_name)
    except:
        pass


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
def volume_with_goss(o, controller, goss_volume_name):
    o.check_or_create_test_tool_volume(goss_volume_name)
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
    c = controller.run_busybox(labels={'a': 'b'})
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

    res = controller.deploy_stack(path, name)
    assert res
    services = controller.get_services(name)
    wait_on_services_status(controller, services)

    yield (name, path, res)

    controller.undeploy_stack(name)
    try_remove_network(controller, name)
    try_remove_network(controller, 'robot_sidecar_for_{}'.format(name))


# Fixtures for entity tests
@fixture(scope='module')
@pytest.mark.usefixtures('stack_infos')
def instance(stack_infos):
    lib = VnfValidator.VnfValidator()
    lib.suite_source = 'bla.robot'
    lib.goss_volume_name = 'goss-helper'
    lib.deployment_name = stack_infos[0]
    lib.descriptor_file = stack_infos[1]
    lib.orchestrator = DockerOrchestrator(lib)
    lib.sut = None
    lib.sidecar = None
    lib.services = [
        Collection().prepare_model(Service(attrs={"ID": "123456789098", "Spec": {"Name": stack_infos[0] + '_sut'}}))]
    return lib


@fixture(scope='module')
def o(instance):
    return DockerOrchestrator(instance)

@fixture
def sut(context='service'):
    return SUT(context, 'sut', 'bla')


@fixture
def sut_deployment():
    return sut(context='deployment')


@fixture
def goss_tool_instance():
    return GossTool()


@fixture
def docker_tool_instance():
    return DockerTool()
