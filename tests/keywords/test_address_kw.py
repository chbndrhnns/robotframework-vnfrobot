import unittest

import os

import pytest
from robot.running import TestSuiteBuilder
from tests import path


def test__address__pass():

    suite = TestSuiteBuilder().build(os.path.join(path, 'fixtures/address.robot'))
    result = suite.run(output=None, variablefile=os.path.join(path, 'fixtures/common.py'))

    assert result.return_code == 0
