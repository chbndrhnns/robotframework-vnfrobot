import re

import pytest

from exc import SetupError, ValidationError
from fixtures.test_data_CommandTarget import command_target_test_data_pass, command_target_test_data_fail, \
    command_target_integration_test_data, command_target_network_context_test_data
from tools.data_structures import SUT
from utils import set_test_data


def test__context__invalid__fail(command_with_instance):
    with pytest.raises(SetupError, match='No SUT'):
        command_with_instance.validate()


@pytest.mark.parametrize('test', command_target_test_data_pass)
def test__validate__pass(command_with_instance, sut, test):
    e = command_with_instance
    e.instance.sut = sut

    set_test_data(e, test)
    e.validate()


@pytest.mark.parametrize('test', command_target_test_data_fail)
def test__validate__fail(command_with_instance, sut, test):
    e = command_with_instance
    e.instance.sut = sut

    set_test_data(e, test)
    with pytest.raises(ValidationError):
        e.validate()


@pytest.mark.parametrize('data', command_target_integration_test_data)
def test__evaluate__pass(command_with_instance, sut, data, docker_tool_instance):
    e = command_with_instance
    e.instance.sut = sut

    set_test_data(e, data.get('test'))
    docker_tool_instance.test_results = data.get('result')
    docker_tool_instance.command = 'run_in_container'
    docker_tool_instance.target = e

    e.evaluate_results(docker_tool_instance)


@pytest.mark.integration
@pytest.mark.parametrize('data', command_target_integration_test_data)
def test__run__pass(command_with_instance, stack, data, service_id):
    e = command_with_instance

    name, path, success = stack
    e.instance.deployment_name = name
    e.instance.sut = SUT('service', 'sut', service_id)

    test = data.get('test')
    set_test_data(e, test)

    e.run_test()


@pytest.mark.integration
@pytest.mark.parametrize('data', command_target_network_context_test_data)
def test__run__network_context__pass(command_with_instance, stack, data, service_id):
    e = command_with_instance

    name, path, success = stack
    e.instance.deployment_name = name
    e.instance.sut = SUT('network', 'm2m', service_id)

    test = data.get('test')
    set_test_data(e, test)

    e.run_test()
