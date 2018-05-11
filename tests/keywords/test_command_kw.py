import unittest

import os

import pytest
from robot.running import TestSuiteBuilder
from tests import path


@pytest.mark.keyword
@pytest.mark.kw_command
def test__command_kw__pass():

    suite = TestSuiteBuilder().build(os.path.join(path, 'fixtures/robot/command.robot'))
    result = suite.run(output=None, variablefile=os.path.join(path, 'fixtures/robot/common.py'))

    assert result.return_code == 0
