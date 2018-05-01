import os

import pytest
from robot.running import TestSuiteBuilder
from tests import path


@pytest.mark.integration
@pytest.mark.keyword
def test_port_pass():

    suite = TestSuiteBuilder().build(os.path.join(path, 'fixtures/robot/port.robot'))
    result = suite.run(output=None, variablefile=os.path.join(path, 'fixtures/robot/common.py'))

    assert result.return_code == 0
