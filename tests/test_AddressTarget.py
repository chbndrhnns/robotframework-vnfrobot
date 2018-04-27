import json

import pytest
from exc import ValidationError, SetupError
from LowLevel import SUT
from fixtures.test_data_GossAddress import goss_results


def test__context__invalid__fail(address_with_instance):
    with pytest.raises(SetupError, match='No SUT'):
        address_with_instance.validate()


def test__validate__pass(address_with_instance, sut):
    e = address_with_instance
    e.instance.sut = sut

    tests = [
        ['www.google.com', 'is', 'reachable']
    ]

    for test in tests:
        e.set_as_dict({
            'entity': test[0],
            'property': test[0],
            'matcher': test[1],
            'value': test[2]})
        e.validate()


def test__validate__wrong_entity__fail(address_with_instance, sut):
    e = address_with_instance
    e.instance.sut = sut

    tests = [
        ['www.google.d', 'is', 'reachable']
    ]

    for test in tests:
        e.set_as_dict({
            'entity': test[0],
            'property': test[0],
            'matcher': test[1],
            'value': test[2]})
        assert not e.validate()


def test__validate__fail(address_with_instance, sut):
    e = address_with_instance
    e.instance.sut = sut

    tests = [
        ['www.google.de', 'isnotoris', 'reachable'],
        ['www.google.de', 'is', 'notorisreachable'],
        ['www.google.de', 'canisnot', 'notorisreachable'],
    ]

    for test in tests:
        with pytest.raises(ValidationError):
            e.set('entity', test[0])
            e.set('property', test[0])
            e.set('matcher', test[1])
            e.set('value', test[2])
            e.validate()


@pytest.mark.parametrize('data, goss_json', goss_results)
def test__evaluate__pass(address_with_instance, sut, data, goss_json):
    e = address_with_instance
    e.instance.sut = sut
    e.test_result = json.loads(goss_json)

    e.evaluate_results()


def test__run__network_context__pass(address_with_instance, stack, network, volume_with_goss):
    e = address_with_instance

    name, path, success = stack
    e.instance.deployment_name = name
    e.instance.sut = SUT(target_type='network', target=network.name, service_id=name + '_sut')
    e.instance.test_volume = volume_with_goss

    test_data = ['www.google.com', 'is', 'reachable']

    e.set('entity', test_data[0])
    e.set('property', test_data[0])
    e.set('matcher', test_data[1])
    e.set('value', test_data[2])

    e.run_test()
