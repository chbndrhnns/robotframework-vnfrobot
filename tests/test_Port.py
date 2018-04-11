import pytest
from pytest import fixture

from exc import ValidationError, SetupError
from modules.context import SUT
from modules.port import validate


@fixture
@pytest.mark.usefixture('instance')
def service_instance(instance, service_context):
    instance.sut = SUT(service_context, 'bla', 'bla')
    return instance


def test__context__invalid__fail(instance):
    instance.sut = SUT('bla', 'bla', 'bla')

    with pytest.raises(SetupError, message='Context type'):
        validate(instance, None, None, None, None)


def test__validate__pass(service_instance):
    tests = [
        ['6379/TCP', 'state', 'is', 'open'],
        ['6379/udp', 'state', 'is', 'open'],
        ['8080', 'state', 'is', 'open'],
        ['8080', 'listening_address', 'is', '::'],
        ['8080', 'listening_address', 'is', '127.0.0.1'],

    ]

    for test in tests:
        validate(service_instance, *test)


def test__validate__fail(service_instance):
    tests = [
        ['66000', 'state', 'is', 'open'],
        ['6379/ABC', 'state', 'is', 'open'],
        ['6379', 'listeningaddress', 'is', '127.0.0.1'],
        ['6379', 'listening_address', 'is', 'open']
    ]

    for test in tests:
        with pytest.raises(ValidationError):
            validate(service_instance, *test)
