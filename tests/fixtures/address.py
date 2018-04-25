import pytest
from pytest import fixture

from modules.address import Address


@fixture
def address_data():
    return {'context': 'network', 'entity': 'www.google.com', 'property': '', 'matcher': 'is', 'value': 'reachable'}


@fixture
def address(address_data):
    address = Address()
    for k, v in address_data.iteritems():
        address.set(k, v)
    return address


@fixture
@pytest.mark.usefixture('instance')
def address_with_instance(address, instance):
    address.instance = instance
    return address
