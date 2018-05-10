import pytest
from pytest import fixture

from ValidationTargets.FileTarget import File


@fixture(scope='module')
def file_data():
    return {'context': 'service', 'entity': '6370/TCP', 'property': 'state', 'matcher': 'is', 'value': 'open'}


@fixture(scope='module')
def file(file_data):
    file = File()
    for k, v in file_data.iteritems():
        file.set(k, v)
    return file


@pytest.mark.usefixture('instance')
@fixture(scope='module')
def file_with_instance(file, instance):
    file.instance = instance
    return file

