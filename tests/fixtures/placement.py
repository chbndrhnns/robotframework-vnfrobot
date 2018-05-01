import pytest
from pytest import fixture

from ValidationTargets.PlacementTarget import Placement


@fixture
def placement_data():
    return {'context': 'deployment', 'entity': 'sut', 'property': 'state', 'matcher': 'is', 'value': 'open'}


@fixture
def placement(port_data):
    placement = Placement()
    for k, v in port_data.iteritems():
        placement.set(k, v)
    return placement


@fixture
@pytest.mark.usefixture('instance')
def placement_with_instance(placement, instance):
    placement.instance = instance
    return placement

