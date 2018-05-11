import pytest
from docker.models.resource import Collection
from docker.models.services import Service

from exc import SetupError, ValidationError
from fixtures.test_data_Placement import placement_target_test_data, placement_target_test_data_fail
from tools.data_structures import SUT
from utils import set_test_data


@pytest.mark.target
def test__context__invalid__fail(placement_with_instance):
    with pytest.raises(SetupError, match='No SUT'):
        placement_with_instance.validate()


@pytest.mark.target
@pytest.mark.parametrize('data', placement_target_test_data)
def test__validate__pass(placement_with_instance, sut, data):
    e = placement_with_instance
    e.instance.sut = sut

    set_test_data(e, data.get('test'))
    e.validate()


@pytest.mark.target
@pytest.mark.parametrize('data', placement_target_test_data_fail)
def test__validate__fail(placement_with_instance, sut, data):
    e = placement_with_instance
    e.instance.sut = sut

    set_test_data(e, data.get('test'))
    with pytest.raises(ValidationError):
        e.validate()


@pytest.mark.target
@pytest.mark.parametrize('data', placement_target_test_data)
def test__evaluate_results__pass(placement_with_instance, docker_tool_instance, sut, data):
    e = placement_with_instance
    e.instance.sut = sut

    set_test_data(e, data.get('test'))
    docker_tool_instance.test_results = data.get('result')
    docker_tool_instance.command = 'placement'

    e.evaluate_results(docker_tool_instance)


@pytest.mark.target
@pytest.mark.integration
@pytest.mark.parametrize('data', placement_target_test_data)
def test__run__pass(placement_with_instance, stack, data):
    e = placement_with_instance

    name, path, success = stack
    e.instance.deployment_name = name
    e.instance.sut = SUT(target_type='service', target=name + '_sut', service_id=name + '_sut')

    test = data.get('test')
    set_test_data(e, test)

    e.run_test()
