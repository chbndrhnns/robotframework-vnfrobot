import pytest
from pytest import fixture

from ValidationTargets.port import Port


@fixture(scope='module')
def port_data():
    return {'context': 'service', 'entity': '6370/TCP', 'property': 'state', 'matcher': 'is', 'value': 'open'}


@fixture(scope='module')
def port(port_data):
    port = Port()
    for k, v in port_data.iteritems():
        port.set(k, v)
    return port


@pytest.mark.usefixture('instance')
@fixture(scope='module')
def port_with_instance(port, instance):
    port.instance = instance
    return port

