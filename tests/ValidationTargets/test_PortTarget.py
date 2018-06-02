import pytest
from ruamel import yaml

from exc import ValidationError, SetupError
from fixtures.test_data_Port import port_target_test_data_pass, port_target_test_data_fail, ports_test_data
from tools.data_structures import SUT
from utils import set_test_data


def test__set_as_dict(port_with_instance):
    port_with_instance.set_as_dict({'value': ' abc'})
    assert port_with_instance.value == 'abc'


@pytest.mark.target
def test__context__invalid__fail(port_with_instance):
    with pytest.raises(SetupError, match='No SUT'):
        port_with_instance.validate()


@pytest.mark.target
@pytest.mark.parametrize('test', port_target_test_data_pass)
def test__validate__pass(port_with_instance, sut, test):
    e = port_with_instance
    e.instance.sut = sut

    set_test_data(e, test)
    e.validate()


@pytest.mark.target
@pytest.mark.parametrize('test', port_target_test_data_fail)
def test__validate__fail(port_with_instance, sut, test):
    e = port_with_instance
    e.instance.sut = sut

    with pytest.raises(ValidationError):
        set_test_data(e, test)
        e.validate()


@pytest.mark.target
@pytest.mark.parametrize('test, data, mapped, out', ports_test_data)
def test__transform__pass(port_with_instance, sut, test, data, mapped, out):
    test = test.get('test')
    e = port_with_instance
    e.instance.sut = sut

    set_test_data(e, test)

    e.validate()
    e._prepare_transform()
    e.transform()

    assert yaml.safe_load(e.transformed_data) == yaml.safe_load(out.get('expected_yaml'))


@pytest.mark.target
@pytest.mark.integration
@pytest.mark.parametrize('test, data, mapped, out', ports_test_data)
def test__run__service_context__pass(port_with_instance, stack, volume_with_goss, test, data, mapped, out):
    e = port_with_instance

    name, path, success = stack
    service = name + '_sut'
    container = e.instance.orchestrator.controller.get_containers_for_service(service)[0]
    e.instance.deployment_name = name
    e.instance.sut = SUT(target_type='service', target=container.name, service_id=service)
    e.instance.test_volume = volume_with_goss

    set_test_data(e, test.get('test'))
