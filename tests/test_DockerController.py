import os

from docker.errors import APIError
import docker
import pytest
from docker.models.services import Service
from docker.models.containers import Container
from pytest import fixture

import namesgenerator
from DockerController import DockerController
from exc import DeploymentError, NotFoundError
from testutils import Result
from tools.archive import Archive
from . import path


@fixture
def goss_test():
    return os.path.join(path, 'fixtures', 'goss-port.yaml')


@fixture
def test_container():
    return 'gosstest_' + namesgenerator.get_random_name()


@fixture
def goss_volume():
    return 'gosstest_' + namesgenerator.get_random_name()


@fixture
def controller():
    return DockerController(base_dir=path)


@fixture
def goss_files():
    return os.path.join(path, 'fixtures', 'goss')


@fixture
def test_stack():
    return 'dc-test', os.path.join(path, 'fixtures', 'dc-test.yml')


def _cleanup_volumes(d, volumes):
    if volumes is None:
        volumes = []
    if isinstance(volumes, str):
        volumes = [volumes]

    for v in volumes:
        res = d._dispatch(['volume', 'rm', v])
        assert len(res.stderr) == 0


def _cleanup_stack(d, stack):
    res = d._dispatch(['stack', 'rm', stack])


def _cleanup(d, containers):
    if containers is None:
        containers = []
    if isinstance(containers, str):
        containers = [containers]

    for container in containers:
        d._dispatch(['service', 'rm', container])
        d._dispatch(['stop', container])
        d._dispatch(['rm', container])


def test__get_stack__fail(controller, test_stack):
    res = controller.find_stack(test_stack[0])

    assert not res


def test__get_stack__pass(controller, test_stack):
    try:
        controller.deploy_stack(test_stack[1], test_stack[0])
        res = controller.find_stack(test_stack[0])
    finally:
        _cleanup_stack(controller, test_stack[0])

    assert res


def test__create_container__pass(controller, test_container):
    controller._dispatch(['run', '-d', '-p', '12345:80', '--name', test_container, 'nginx'])
    _cleanup(controller, test_container)


def test__run_sidecar__pass(controller, test_container):
    _cleanup(controller, test_container)

    controller._dispatch(['run', '-d', '-p', '12345:80', '--name', test_container, 'nginx'])

    result = controller.run_sidecar(image='subfuzion/netcat', command='-z 127.0.0.1 12345 ; echo $?')
    _cleanup(controller, test_container)

    assert result == Result.PASS


def test__list_containers__pass(controller):
    controller = DockerController(base_dir=path)

    result = controller.get_containers()

    assert len(result) > 0


def test__get_env__container(controller, test_container):
    _cleanup(controller, test_container)

    try:
        res = controller._dispatch(['run', '-d', '--name', test_container, 'nginx'])
        assert len(res.stderr) == 0
        env = controller.get_env(test_container)
        assert isinstance(env, list)
        assert [e for e in env if 'PATH' in e]
    finally:
        _cleanup(controller, test_container)


def test__get_env__service(controller):
    stack_name = 'test-stack'
    service = 'sut'

    service_id = '{}_{}'.format(stack_name, service)

    _cleanup(controller, service_id)

    try:
        controller._dispatch(['stack', 'deploy', '-c', os.path.join(path, 'fixtures', 'dc-test.yml'), stack_name])
        env = controller.get_env(service_id)
    finally:
        _cleanup(controller, service_id)

    assert isinstance(env, list)
    assert [e for e in env if 'PATH' in e]


def test__find_service__pass(controller):
    stack_name = 'test-stack'
    service = 'sut'

    service_id = '{}_{}'.format(stack_name, service)

    _cleanup(controller, service_id)

    controller._dispatch(['stack', 'deploy', '-c', os.path.join(path, 'fixtures', 'dc-test.yml'), stack_name])
    service = controller.get_service(service_id)

    assert isinstance(service, Service)

    # cleanup(controller, service_id)


def test__create_goss_volume(controller, goss_volume):
    try:
        res = controller.create_volume(goss_volume)
        assert len(res.stderr) == 0
    finally:
        _cleanup_volumes(controller, goss_volume)


def test__add_data_to_volume(controller, goss_volume, goss_files):
    try:
        res = controller.create_volume(goss_volume)
        assert len(res.stderr) == 0

        controller.add_data_to_volume(goss_volume, goss_files)
        res = controller.list_files_on_volume(goss_volume)
        assert 'goss-linux-amd64' in res.stdout
        assert 'goss-linux-386' in res.stdout
    finally:
        _cleanup_volumes(controller, goss_volume)


def test__put_file__pass(controller, goss_test):
    c = controller._docker.containers.run('busybox', 'true', detach=True)

    try:
        controller.put_file(c.id, goss_test)
    except (DeploymentError, NotFoundError) as exc:
        pytest.fail(exc)


def test__put_file__file_not_found__fail(controller, goss_test):
    c = controller._docker.containers.run('busybox', 'true', detach=True)

    with pytest.raises(NotFoundError):
        controller.put_file(c.id, 'goss.yaml')


def test__put_file__destination_does_not_exist__fail(controller, goss_test):
    c = controller._docker.containers.run('busybox', 'true', detach=True)

    with pytest.raises(DeploymentError):
        controller.put_file(c.id, goss_test, '/goss/goss.yaml')


def test__get_file__pass(controller):
    c = controller._docker.containers.run('busybox', 'true', detach=True)

    try:
        f = controller.get_file(c.id, '/etc/', 'hosts')
        assert len(f) > 0
        assert '127.0.0.1' in f
    except (DeploymentError, NotFoundError) as exc:
        pytest.fail(exc)


def test__get_file__not_found__fail(controller):
    c = controller._docker.containers.run('busybox', 'true', detach=True)

    with pytest.raises(DeploymentError):
        f = controller.get_file(c.id, '/etc/', 'hostsbla')


def test__run_goss_in_container__pass():
    pass


def test__inject_goss_data_into_stack_container__pass(controller, test_stack, goss_file):
    pytest.fail('not implemented')

    name = test_stack[0]
    path = test_stack[1]

    service = 'sut'

    service_id = '{}_{}'.format(name, service)

    try:
        res = controller.deploy_stack(path, name)
        assert res

        c = controller.get_containers_for_service(service_id)
        assert len(c) > 0
        container = c[0]






    finally:
        # _cleanup_stack(controller, name)
        pass
