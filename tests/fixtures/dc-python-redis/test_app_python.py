import os

import pytest
from robot.running import TestSuiteBuilder
from tests import path


@pytest.mark.descriptor
def test__address__pass():

    suite = TestSuiteBuilder().build(os.path.join(path, 'fixtures/dc-python-redis/app1.robot'))
    result = suite.run(output=None)

    assert result.return_code == 0
