import os

from robot.running import TestSuiteBuilder


def test__enforce_validation():
    suite = TestSuiteBuilder().build(os.path.join(os.getcwd(), 'tests', 'fixtures', 'robot', 'context_only.robot'))
    result = suite.run(output=None, variablefile=os.path.join('fixtures/robot/common.py'))

    assert result.statistics.total.all.failed > 0
