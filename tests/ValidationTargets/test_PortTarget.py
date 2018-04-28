import pytest
from ruamel import yaml

from exc import ValidationError, SetupError
from fixtures.test_data_Port import port_target_test_data_pass, port_target_test_data_fail, ports_test_data
from tools.data_structures import SUT


def test__context__invalid__fail(port_with_instance):
    with pytest.raises(SetupError, match='No SUT'):
        port_with_instance.validate()


@pytest.mark.parametrize('test', port_target_test_data_pass)
def test__validate__pass(port_with_instance, sut, test):
    p = port_with_instance
    p.instance.sut = sut

    p.set('entity', test[0])
    p.set('property', test[1])
    p.set('matcher', test[2])
    p.set('value', test[3])
    p.validate()


@pytest.mark.parametrize('test', port_target_test_data_fail)
def test__validate__fail(port_with_instance, sut, test):
    p = port_with_instance
    p.instance.sut = sut

    with pytest.raises(ValidationError):
        p.set('entity', test[0])
        p.set('property', test[1])
        p.set('matcher', test[2])
        p.set('value', test[3])
        p.validate()


@pytest.mark.parametrize('test, data, mapped, out', ports_test_data)
def test__transform__pass(port_with_instance, sut, test, data, mapped, out):
    test = test.get('test')
    e = port_with_instance
    e.instance.sut = sut
    e.set_as_dict({
        'entity': test[0],
        'property': test[1],
        'matcher': test[2],
        'value': test[3]
    })

    e.validate()
    e.transform()

    assert yaml.safe_load(e.transformed_data) == yaml.safe_load(out.get('expected_yaml'))


@pytest.mark.parametrize('test, data, mapped, out', ports_test_data)
def test__run__service_context__pass(port_with_instance, stack, volume_with_goss, test, data, mapped, out):
    e = port_with_instance

    name, path, success = stack
    service = name + '_sut'
    container = e.instance.docker_controller.get_containers_for_service(service)[0]
    e.instance.deployment_name = name
    e.instance.sut = SUT(target_type='service', target=container.name, service_id=service)
    e.instance.test_volume = volume_with_goss

    test = test.get('test')

    e.set('entity', test[0])
    e.set('property', test[1])
    e.set('matcher', test[2])
    e.set('value', test[3])

# TODO hier weitermachen