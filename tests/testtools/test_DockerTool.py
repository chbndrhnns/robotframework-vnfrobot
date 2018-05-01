import pytest
from docker.models.nodes import Node
from pytest import fixture

from exc import NotFoundError
from testtools.DockerTool import DockerTool
from tools.data_structures import SUT


@fixture(scope='module')
def dockertool(controller, dummy_sut):
    return DockerTool(controller=controller, sut=dummy_sut)


@fixture
def env_return_value():
    return [
        "PATH=/usr/bin",
        "VERSION=1.0"
    ]


@fixture
def container_labels():
    return {
        'a': 'b',
        'com.docker.swarm.node.id': 'abc'
    }


@fixture
def node_labels():
    return {'node.id': 'hampelmann'}


@fixture
def container(controller, container_labels):
    c = controller.run_busybox(labels=container_labels)
    yield c
    controller._kill_and_delete_container(c.name)


@fixture
def sut(container):
    return SUT(target_type='service', target=container.name, service_id=container.name)


@fixture(scope='module')
def dummy_sut():
    return SUT(target_type='service', target='', service_id='')


@pytest.mark.mock
def test__get_env_vars__pass(mocker, dockertool, env_return_value):
    def side_effect(*args, **kwargs):
        return env_return_value

    mocker.patch.object(dockertool, 'controller')
    dockertool.controller.get_container_config.side_effect = side_effect

    # Test
    dockertool.env_vars()

    dockertool.controller.get_container_config.assert_called_once()
    assert len(dockertool.test_results) == 2


@pytest.mark.mock
def test__get_env_vars__fail(mocker, dockertool):
    mocker.patch.object(dockertool, 'controller')
    dockertool.controller.get_container_config.side_effect = NotFoundError

    # Test
    with pytest.raises(NotFoundError):
        dockertool.env_vars()

    dockertool.controller.get_container_config.assert_called_once()


@pytest.mark.mock
def test__get_container_labels__pass(mocker, dockertool, container_labels):
    mocker.patch.object(dockertool, 'controller')
    dockertool.controller.get_container_config.return_value = container_labels

    # Test
    actual = dockertool.get_container_labels()

    dockertool.controller.get_container_config.assert_called_once()
    assert len(actual) == 1
    assert actual == container_labels


@pytest.mark.mock
def test__get_container_labels__pass(mocker, dockertool):
    mocker.patch.object(dockertool, 'controller')
    dockertool.controller.get_container_config.side_effect = NotFoundError

    # Test
    with pytest.raises(NotFoundError):
        dockertool.get_container_labels()

    dockertool.controller.get_container_config.assert_called_once()


@pytest.mark.integration
def test__get_container_labels2__pass(dockertool, sut, container_labels):
    dockertool.sut = sut
    # Test
    dockertool.get_container_labels()

    assert dockertool.test_results == container_labels


@pytest.mark.integration
def test__get_container_labels__fail(dockertool):
    dockertool.sut = SUT('bla', 'bla', 'bla')

    # Test
    with pytest.raises(NotFoundError):
        dockertool.get_container_labels()


