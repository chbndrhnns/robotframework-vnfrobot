import pytest
from docker.models.containers import Container
from docker.models.services import Service

from DockerController import DockerController
from exc import DeploymentError, NotFoundError
from tools.testutils import Result
from . import path


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
    if isinstance(containers, basestring):
        containers = [containers]

    for container in containers:
        d._dispatch(['service', 'rm', container])
        d._dispatch(['stop', container])
        d._dispatch(['rm', '-f', container])


def test__get_stack__fail(controller, stack_infos):
    res = controller.find_stack(stack_infos[0])

    assert not res


def test__get_stack__pass(controller, stack):
    res = controller.find_stack(stack[0])
    assert res


def test__create_container__pass(controller, container_name):
    controller._dispatch(['run', '-d', '-p', '12345:80', '--name', container_name, 'nginx'])
    _cleanup(controller, container_name)


def test__list_containers__pass(controller, containers):
    controller = DockerController(base_dir=path)

    assert isinstance(containers, list)
    assert len(containers) > 0


def test__get_env__container(controller, container):
    env = controller.get_env(container.name)
    assert isinstance(env, list)
    assert [e for e in env if 'PATH' in e]


def test__get_env__service(controller, stack, service_id):
    env = controller.get_env(service_id)

    assert isinstance(env, list)
    assert [e for e in env if 'PATH' in e]


def test__find_service__pass(controller, stack, service_id):
    service = controller.get_service(service_id)

    assert isinstance(service, Service)


def test__create_goss_volume(controller, volume):
    assert not volume[0].stderr


def test__add_data_to_volume(controller, volume, goss_files):
    name = volume[1]
    controller.add_data_to_volume(name, goss_files)
    res = controller.list_files_on_volume(name)
    assert 'goss-linux-amd64' in res.stdout
    assert 'goss-linux-386' in res.stdout


def test__put_file__pass(controller, container, gossfile):
    try:
        controller.put_file(container.id, gossfile)
    except (DeploymentError, NotFoundError) as exc:
        pytest.fail(exc)


def test__put_file__file_not_found__fail(controller, container, gossfile):
    with pytest.raises(NotFoundError):
        controller.put_file(container.id, 'goss.yaml')


def test__put_file__destination_does_not_exist__fail(controller, container, gossfile):
    with pytest.raises(DeploymentError):
        controller.put_file(container.id, gossfile, '/goss/goss.yaml')


def test__get_file__pass(controller, container):
    try:
        f = controller.get_file(container.id, '/etc/', 'hosts')
        assert len(f) > 0
        assert '127.0.0.1' in f
    except (DeploymentError, NotFoundError) as exc:
        pytest.fail(exc)


def test__get_file__not_found__fail(container, controller):
    with pytest.raises(DeploymentError):
        f = controller.get_file(container.id, '/etc/', 'hostsbla')


def test__execute__invalid_container_object__fail(controller):
    c = Container()
    with pytest.raises(ValueError):
        controller.execute(c, '/bin/bash')


def test__execute__no_command__fail(controller):
    container = Container()
    with pytest.raises(ValueError):
        controller.execute(container, '/bin/bash')


def test__execute_in_stack__pass(controller, stack, service_id):
    string = 'hello'
    try:
        containers = controller.get_containers_for_service(service_id)
        res = controller.execute(containers[0], ['sh', '-c', '\'echo "{}"\''.format(string)])
        assert string in res
    finally:
        _cleanup(controller, service_id)


def test__run_sidecar__pass(sidecar):
    controller = sidecar.get('controller')
    name = sidecar.get('name')

    res = controller.run_sidecar(name=name, command='ls')

    assert 'bin' in res


def test__run_sidecar__invalid_container__fail(sidecar):
    controller = sidecar.get('controller')
    name = sidecar.get('name')

    with pytest.raises(DeploymentError, match='Image '):
        controller.run_sidecar(name=name, command='ls', image='blablubnotexisting')


def test__run_sidecar__stderr__fail(sidecar):
    controller = sidecar.get('controller')
    name = sidecar.get('name')

    with pytest.raises(DeploymentError, match='returned non-zero exit status'):
        controller.run_sidecar(name=name, command='uname -xxx')


def test__run_sidecar__goss_volume_ok__pass(sidecar, goss_volume):
    controller = sidecar.get('controller')
    name = sidecar.get('name')

    volumes = {
        goss_volume: {
            'bind': '/goss',
            'mode': 'ro'
        }
    }

    res = controller.run_sidecar(name=name, volumes=volumes, command='ls /goss')

    assert '' in res


def test__run_sidecar__invalid_network__fail(sidecar):
    controller = sidecar.get('controller')
    name = sidecar.get('name')

    with pytest.raises(DeploymentError, match='Could not attach to network'):
        controller.run_sidecar(name=name, network='bla', command='ping -W1 -c1 8.8.8.8')


def test__run_sidecar__network_ok__pass(sidecar, network):
    controller = sidecar.get('controller')
    name = sidecar.get('name')
    assert 'robot' in network.name

    res = controller.run_sidecar(name=name, network=network.name, command='ping -W1 -c1 8.8.8.8')
    assert '8.8.8.8' in res


def test__run_sidecar__attach_to_deployment_network__pass(sidecar, stack_infos, network, service_id):
    controller = sidecar.get('controller')
    sidecar_name = sidecar.get('name')
    deployment_name = stack_infos[0]


    res = controller.run_sidecar(name=name, network='robot', command='ping -W1 -c1 8.8.8.8')
    assert '8.8.8.8' in res

    ### TODO: Hier geht's weiter.


def test__connect_container_to_network__pass(controller, stack, network, service_id):
    res = controller.connect_container_to_service(service_id, network.name)
    assert res


def test__inject_goss_data_into_stack_container__pass(controller, stack_infos, gossfile):
    name = stack_infos[0]
    path = stack_infos[1]

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
