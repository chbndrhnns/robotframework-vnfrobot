import pytest
from pytest import fixture

from modules.port import Port


@fixture
def port_data():
    return {'context': 'service', 'entity': '6370/TCP', 'property': 'state', 'matcher': 'is', 'value': 'open'}


@fixture
def port(port_data):
    port = Port()
    for k, v in port_data.iteritems():
        port.set(k, v)
    return port


@fixture
@pytest.mark.usefixture('instance')
def port_with_instance(port, instance):
    port.instance = instance
    return port

