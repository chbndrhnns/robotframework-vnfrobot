import pytest
from pytest import fixture

from ValidationTargets.PortTarget import Port


@fixture(scope='module')
def port_data():
    return {'context': 'service', 'entity': '6370/TCP', 'property': 'state', 'matcher': 'is', 'value': 'open'}


@pytest.mark.usefixture('instance')
@fixture(scope='module')
def port_with_instance(port_data, instance):
    port = Port(instance)
    for k, v in port_data.iteritems():
        port.set(k, v)
    return port

