import pytest
from exc import ValidationError, SetupError


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
        e.validate()


def test__validate__fail(address_with_instance, sut):
    e = address_with_instance
    e.instance.sut = sut

    tests = [
        ['66000', 'state', 'is', 'open'],
        ['6379/ABC', 'state', 'is', 'open'],
        ['6379', 'listeningaddress', 'is', '127.0.0.1'],
        ['6379', 'listening_address', 'is', 'open']
    ]

    for test in tests:
        with pytest.raises(ValidationError):
            e.set('entity', test[0])
            e.set('property', test[1])
            e.set('matcher', test[2])
            e.set('value', test[3])
            e.validate()
