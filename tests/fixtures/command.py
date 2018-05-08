import pytest
from pytest import fixture

from ValidationTargets.AddressTarget import Address
from ValidationTargets.CommandTarget import Command


@fixture(scope='module')
def command_data():
    return {
        'context': 'service',
        'entity': 'sh --version',
        'property': 'stdout',
        'matcher': 'contains',
        'value': 'Free'
    }


@fixture(scope='module')
def command(command_data):
    address = Command()
    for k, v in command_data.iteritems():
        address.set(k, v)
    return address


@fixture(scope='module')
@pytest.mark.usefixture('instance')
def command_with_instance(command, instance):
    command.instance = instance
    return command
