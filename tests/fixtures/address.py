import pytest
from pytest import fixture

from ValidationTargets.address import Address


@fixture(scope='module')
def address_data():
    return {'context': 'network', 'entity': 'www.google.com', 'property': '', 'matcher': 'is', 'value': 'reachable'}


@fixture(scope='module')
def address(address_data):
    address = Address()
    for k, v in address_data.iteritems():
        address.set(k, v)
    return address


@fixture(scope='module')
@pytest.mark.usefixture('instance')
def address_with_instance(address, instance):
    address.instance = instance
    return address
