import pytest
from pytest import fixture

from ValidationTargets.FileTarget import File


@fixture(scope='module')
def file_data():
    return {'context': 'service', 'entity': '6370/TCP', 'property': 'state', 'matcher': 'is', 'value': 'open'}


@pytest.mark.usefixture('instance')
@fixture(scope='module')
def file_with_instance(file_data, instance):
    f = File(instance)
    for k, v in file_data.iteritems():
        f.set(k, v)
    return f
