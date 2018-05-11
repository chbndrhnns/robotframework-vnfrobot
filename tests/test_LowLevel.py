import logging

import pytest
from mock import patch, MagicMock
from unittest2 import TestCase

from robot.api import TestSuite
from robot.running import Keyword

from DockerController import DockerController
from tools.testutils import run_keyword_tests, Result


@pytest.mark.skip(reason="Legacy")
class LowLevelTest(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.settings = {'log_level': logging.DEBUG}

    def setUp(self):
        self.suite = TestSuite('Test low level keywords')
        self.suite.resource.imports.library('VnfValidator')

    def tearDown(self):
        pass

    def test__set_context__pass(self):
        tests = [
            Keyword(name=u'Set application context to node_1'),
            Keyword(name=u'Set network context to node_1'),
            Keyword(name=u'Set node context to node_1'),
            Keyword(name=u'Set service context to node_1'),
        ]

        with patch('DockerController.DockerController') as mock_controller:
            mock_controller = MagicMock(DockerController)
            run_keyword_tests(test_instance=self, tests=tests, expected_result=Result.PASS)

    def test__set_context__wrong_context_type__fail(self):
        test = self.suite.tests.create(name=u'Test context')

        test.keywords.append(Keyword(name=u'Set app context to bla'))
        result = self.suite.run()

        self.assertIn("Invalid context given", result.suite.tests[0].message)

    def test__port__pass(self):
        self.suite.keywords.append(Keyword(name='Set network context to node_1', type='setup'))

        tests = [
            Keyword(name=u'Port 80: state is open'),
            Keyword(name=u'Port 80/TCP: state is open'),
            Keyword(name=u'Port 80/UDP: state is open'),
            Keyword(name=u'Port 80/UDP: state is closed'),
        ]
        run_keyword_tests(test_instance=self, tests=tests, expected_result=Result.PASS)

    def test__port__invalid_property__fail(self):
        self.suite.keywords.append(Keyword(name='Set network context to node_1', type='setup'))

        tests = [
            Keyword(name=u'Port 80: stateful is open'),
        ]
        with patch('ValidationTargets.port.exc.SetupError.ROBOT_EXIT_ON_FAILURE', False):
            run_keyword_tests(test_instance=self, setup=None, tests=tests, expected_result=Result.FAIL,
                              expected_message=u'ValidationError: Property')

    def test__port__invalid_port__fail(self):
        self.suite.keywords.append(Keyword(name='Set network context to node_1', type='setup'))

        tests = [
            Keyword(name=u'Port abc: stateful is open'),
            Keyword(name=u'Port abc: stateful is open'),
        ]
        with patch('ValidationTargets.port.exc.SetupError.ROBOT_EXIT_ON_FAILURE', False):
            run_keyword_tests(test_instance=self, setup=None, tests=tests, expected_result=Result.FAIL,
                              expected_message=u'ValidationError: Port')

    def test__port__invalid_value__fail(self):
        self.suite.keywords.append(Keyword(name='Set network context to node_1', type='setup'))

        tests = [
            Keyword(name=u'Port 80: state is openedd'),
        ]
        with patch('ValidationTargets.port.exc.SetupError.ROBOT_EXIT_ON_FAILURE', False):
            run_keyword_tests(test_instance=self, setup=None, tests=tests, expected_result=Result.FAIL,
                              expected_message=u'ValidationError: Value')
