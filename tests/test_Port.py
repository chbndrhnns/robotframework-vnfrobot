import unittest

import os

import pytest
from robot.running import TestSuiteBuilder

path = os.path.dirname(os.path.realpath(__file__))


def test_port_pass():
    suite = TestSuiteBuilder().build(os.path.join(path, 'fixtures/port.robot'))
    result = suite.run(output=None)

    assert result.return_code == 0
