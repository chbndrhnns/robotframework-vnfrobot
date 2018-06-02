import pytest
from pytest import fixture

from ValidationTargets.LogsTarget import LogsTarget


@fixture(scope='module')
def logs_data():
    return {
        'context': 'service',
        'entity': '',
        'property': '',
        'matcher': 'contains',
        'value': 'server app2_awesome.1'
    }


@fixture(scope='module')
@pytest.mark.usefixture('instance')
def logs_with_instance(command_data, instance):
    logs = LogsTarget(instance)
    for k, v in command_data.iteritems():
        logs.set(k, v)
    return logs
