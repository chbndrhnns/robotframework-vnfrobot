import os
from pytest import fixture

import namesgenerator
from . import path

from DockerController import DockerController


@fixture(scope='module')
def service_id(stack_infos):
    return '{}_sut'.format(stack_infos[0])


@fixture(scope='module')
def containers(controller, service_id, stack):
    return controller.get_containers_for_service(service_id)

@fixture
def volume(controller, goss_volume):
    res = controller.create_volume(goss_volume)
    yield (res, goss_volume)
    controller.delete_volume(goss_volume)


@fixture
def gossfile():
    return os.path.join(path, 'fixtures', 'goss-port.yaml')


@fixture
def container_name():
    return 'gosstest_' + namesgenerator.get_random_name()


@fixture
def goss_volume():
    return 'gosstest_' + namesgenerator.get_random_name()


@fixture(scope='session')
def controller():
    assert path is not None
    return DockerController(base_dir=path)


@fixture
def container(controller, goss_volume):
    c = controller.run_busybox()
    yield c
    try:
        c.kill()
        c.remove()
    except Exception:
        pass


@fixture
def goss_files():
    return os.path.join(path, 'fixtures', 'goss')


@fixture(scope='module')
def stack_infos():
    return 'dc-test', os.path.join(path, 'fixtures', 'dc-test.yml')


@fixture(scope='module')
def stack(controller, stack_infos):
    name = stack_infos[0]
    path = stack_infos[1]

    yield (name, path, controller.deploy_stack(path, name))

    controller.undeploy_stack(name)
