import os

import pytest
from robot.running import TestSuiteBuilder
from tests import path


@pytest.mark.integration
@pytest.mark.descriptor
def test__address__pass():

    suite = TestSuiteBuilder().build(os.path.join(path, 'fixtures/dc-haproxy/dc-haproxy.robot'))
    result = suite.run(output=None)

    assert result.return_code == 0
