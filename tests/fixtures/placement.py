import pytest
from pytest import fixture

from ValidationTargets.PlacementTarget import Placement


@fixture
def placement_data():
    return {'context': 'deployment', 'entity': 'sut', 'property': 'state', 'matcher': 'is', 'value': 'open'}


@fixture
@pytest.mark.usefixture('instance')
def placement_with_instance(placement_data, instance):
    p = Placement(instance)
    for k, v in placement_data.iteritems():
        p.set(k, v)
    return p

