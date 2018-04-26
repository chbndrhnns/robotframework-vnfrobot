import pytest
from exc import ValidationError, SetupError


def test__context__invalid__fail(port_with_instance):
    with pytest.raises(SetupError, match='No SUT'):
        port_with_instance.validate()


def test__validate__pass(port_with_instance, sut):
    p = port_with_instance
    p.instance.sut = sut

    tests = [
        ['6379/TCP', 'state', 'is', 'open'],
        ['6379/udp', 'state', 'is', 'open'],
        ['8080', 'state', 'is', 'open'],
        ['8080', 'listening address', 'is', '::'],
        ['8080', 'listening address', 'is', '127.0.0.1'],

    ]

    for test in tests:
        p.set('entity', test[0])
        p.set('property', test[1])
        p.set('matcher', test[2])
        p.set('value', test[3])
        p.validate()


def test__validate__fail(port_with_instance, sut):
    p = port_with_instance
    p.instance.sut = sut

    tests = [
        ['66000', 'state', 'is', 'open'],
        ['6379/ABC', 'state', 'is', 'open'],
        ['6379', 'listeningaddress', 'is', '127.0.0.1'],
        ['6379', 'listening_address', 'is', 'open']
    ]

    for test in tests:
        with pytest.raises(ValidationError):
            p.set('entity', test[0])
            p.set('property', test[1])
            p.set('matcher', test[2])
            p.set('value', test[3])
            p.validate()