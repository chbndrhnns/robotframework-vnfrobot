import os

import pytest
from robot.running import TestSuiteBuilder
from tests import path


@pytest.mark.kw_variable
@pytest.mark.keyword
def test__variable_kw__pass():
    suite = TestSuiteBuilder().build(os.path.join(path, 'fixtures/robot/variable.robot'))
    result = suite.run(output=None, variablefile=os.path.join(path, 'fixtures/robot/common.py'))

    assert result.return_code == 0
