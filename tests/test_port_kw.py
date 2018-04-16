import unittest

import os

import pytest
from robot.running import TestSuiteBuilder
from . import path


def test_port_pass():

    suite = TestSuiteBuilder().build(os.path.join(path, 'fixtures/port.robot'))
    result = suite.run(output=None, variablefile=os.path.join(path, 'fixtures/common.py'))

    assert result.return_code == 0