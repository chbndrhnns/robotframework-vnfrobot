import pytest

from exc import SetupError, ValidationError
from fixtures.test_data_LogsTarget import logs_target_test_data_pass, logs_target_test_data_fail, \
    logs_target_integration_test_data
from tools.data_structures import SUT
from utils import set_test_data


@pytest.mark.target
def test__context__invalid__fail(logs_with_instance):
    with pytest.raises(SetupError, match='No SUT'):
        logs_with_instance.validate()


@pytest.mark.target
@pytest.mark.parametrize('test', logs_target_test_data_pass)
def test__validate__pass(logs_with_instance, sut, test):
    e = logs_with_instance
    e.instance.sut = sut

    set_test_data(e, test)
    e.validate()


@pytest.mark.target
@pytest.mark.parametrize('test', logs_target_test_data_fail)
def test__validate__fail(logs_with_instance, sut, test):
    e = logs_with_instance
    e.instance.sut = sut

    set_test_data(e, test)
    with pytest.raises(ValidationError):
        e.validate()


@pytest.mark.target
@pytest.mark.parametrize('data', logs_target_integration_test_data)
def test__evaluate__pass(logs_with_instance, sut, data, docker_tool_instance):
    e = logs_with_instance
    e.instance.sut = sut

    set_test_data(e, data.get('test'))
    docker_tool_instance.test_results = data.get('result')
    docker_tool_instance.command = 'logs'
    docker_tool_instance.target = e

    e.evaluate_results(docker_tool_instance)


@pytest.mark.target
@pytest.mark.integration
@pytest.mark.parametrize('data', logs_target_integration_test_data)
def test__run__pass(logs_with_instance, stack, data):
    e = logs_with_instance

    name, path, success = stack
    e.instance.deployment_name = name
    e.instance.sut = SUT('service', 'sut', '{}_sut'.format(name))

    test = data.get('test')
    set_test_data(e, test)

    e.run_test()
