import os
from robot.running import TestSuiteBuilder
from . import path


def test__variable__pass():
    suite = TestSuiteBuilder().build(os.path.join(path, 'fixtures/variable.robot'))
    result = suite.run_detached(output=None)

    assert result.return_code == 0
