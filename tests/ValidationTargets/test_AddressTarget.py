import json

import pytest
from docker.models.resource import Collection
from docker.models.services import Service
from ruamel import yaml

from exc import ValidationError, SetupError
from VnfValidator import SUT
from fixtures.test_data_Address import goss_results, addresses_test_data
from utils import set_test_data


@pytest.mark.target
def test__context__invalid__fail(address_with_instance):
    with pytest.raises(SetupError, match='No SUT'):
        address_with_instance.validate()


@pytest.mark.target
def test__validate__pass(address_with_instance, sut):
    e = address_with_instance
    e.instance.sut = sut

    tests = [
        ['www.google.com', 'www.google.com', 'is', 'reachable']
    ]

    for test in tests:
        set_test_data(e, test)
        e.validate()


@pytest.mark.target
def test__validate__wrong_entity__fail(address_with_instance, sut):
    e = address_with_instance
    e.instance.sut = sut

    tests = [
        ['www.google.d', 'www.google.d', 'is', 'reachable']
    ]

    for test in tests:
        set_test_data(e, test)
        with pytest.raises(ValidationError):
            assert not e.validate()


@pytest.mark.target
def test__validate__fail(address_with_instance, sut):
    e = address_with_instance
    e.instance.sut = sut

    tests = [
        ['www.google.de', 'www.google.de', 'isnotoris', 'reachable'],
        ['www.google.de', 'www.google.de', 'is', 'notorisreachable'],
        ['www.google.de', 'www.google.de', 'canisnot', 'notorisreachable'],
    ]

    for test in tests:
        with pytest.raises(ValidationError):
            set_test_data(e, test)
            e.validate()


@pytest.mark.target
@pytest.mark.parametrize('test, goss_result', goss_results)
def test__evaluate__pass(address_with_instance, goss_tool_instance, sut, test, goss_result):
    e = address_with_instance
    e.instance.sut = sut

    goss_tool_instance.test_results = json.loads(goss_result)

    e.evaluate_results(goss_tool_instance)

@pytest.mark.target
@pytest.mark.parametrize('test, data, mapped, out', addresses_test_data)
def test__transform__pass(address_with_instance, sut, test, data, mapped, out):
    test = test.get('test')
    e = address_with_instance
    e.instance.sut = sut
    set_test_data(e, test)
    e.validate()
    e._prepare_transform()
    e.transform()

    assert yaml.safe_load(e.transformed_data) == yaml.safe_load(out.get('expected_yaml'))


@pytest.mark.integration
@pytest.mark.target
@pytest.mark.parametrize('test, data, mapped, out', addresses_test_data)
def test__run__network_context__pass(address_with_instance, stack, network, volume_with_goss, test, data, mapped, out):
    e = address_with_instance

    name, path, success = stack
    e.instance.deployment_name = name

    e.instance.sut = SUT(target_type='network', target=network.name, service_id=name + '_m2m')
    e.instance.test_volume = volume_with_goss

    test = test.get('test')
    set_test_data(e, test)

    e.run_test()
