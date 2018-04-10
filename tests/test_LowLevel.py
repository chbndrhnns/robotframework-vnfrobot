import logging
import pytest
from mock import patch
from robot.running.model import Variable

from unittest2 import TestCase

from robot.api import TestSuite
from robot.running import Keyword

from testutils import run_keyword_tests, Result


class LowLevelTest(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.settings = {'log_level': logging.DEBUG}

    def setUp(self):
        self.suite = TestSuite('Test low level keywords')
        self.suite.resource.imports.library('LowLevel')
        self.suite.resource.variables.append(Variable('${USE_DEPLOYMENT}', 'Bla'))

    def tearDown(self):
        pass

    def test__set_context__pass(self):
        tests = [
            Keyword(name=u'Set application context to node_1'),
            Keyword(name=u'Set network context to node_1'),
            Keyword(name=u'Set node context to node_1'),
            Keyword(name=u'Set service context to node_1'),
        ]

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
        with patch('modules.port.exc.SetupError.ROBOT_EXIT_ON_FAILURE', False):
            run_keyword_tests(test_instance=self, setup=None, tests=tests, expected_result=Result.FAIL,
                              expected_message=u'ValidationError: Property')

    def test__port__invalid_port__fail(self):
        self.suite.keywords.append(Keyword(name='Set network context to node_1', type='setup'))

        tests = [
            Keyword(name=u'Port abc: stateful is open'),
            Keyword(name=u'Port abc: stateful is open'),
        ]
        with patch('modules.port.exc.SetupError.ROBOT_EXIT_ON_FAILURE', False):
            run_keyword_tests(test_instance=self, setup=None, tests=tests, expected_result=Result.FAIL,
                              expected_message=u'ValidationError: Port')

    def test__port__invalid_value__fail(self):
        self.suite.keywords.append(Keyword(name='Set network context to node_1', type='setup'))

        tests = [
            Keyword(name=u'Port 80: state is openedd'),
        ]
        with patch('modules.port.exc.SetupError.ROBOT_EXIT_ON_FAILURE', False):
            run_keyword_tests(test_instance=self, setup=None, tests=tests, expected_result=Result.FAIL,
                              expected_message=u'ValidationError: Value')

    def test__variable__invalid_var__fail(self):
        self.suite.keywords.append(Keyword(name='Set service context to node_1', type='setup'))

        tests = [
            Keyword(name=u'Variable 80: is b'),
            Keyword(name=u'Variable abc: is b'),
            Keyword(name=u'Variable A-B: is b'),
        ]
        with patch('modules.variable.exc.SetupError.ROBOT_EXIT_ON_FAILURE', False):
            run_keyword_tests(test_instance=self, setup=None, tests=tests, expected_result=Result.FAIL,
                              expected_message=u'ValidationError: Value')

    def test__variable__pass(self):
        self.suite.keywords.append(Keyword(name='Set service context to node_1', type='setup'))

        tests = [
            Keyword(name=u'Variable PATH: contains /usr/bin'),
            Keyword(name=u'Variable PATH: is /usr/bin'),
            Keyword(name=u'Variable PATH: is "/usr/bin"'),
            Keyword(name=u'Variable PATH: is \'/usr/bin\''),
            Keyword(name=u'Variable NGINX_VERSION: contains 2.0.0beta1'),
            Keyword(name=u'Variable NGINX_VERSION: is 2.0.0beta1'),
        ]
        with patch('LowLevel.orchestrator.DockerController.get_env', return_value=["PATH=/usr/bin", "NGINX_VERSION=2.0.0beta1"]):
            run_keyword_tests(test_instance=self, tests=tests, expected_result=Result.PASS)

    def test__variable__variable_does_not_exist__fail(self):
        self.suite.keywords.append(Keyword(name='Set service context to node_1', type='setup'))

        tests = [
            Keyword(name=u'Variable PTH: contains /usr/bin'),
        ]
        with patch('LowLevel.orchestrator.DockerController.get_env', return_value=["PATH=/usr/bin"]):
            run_keyword_tests(test_instance=self, tests=tests, expected_result=Result.FAIL)

    def test__variable__invalid_value__fail(self):
        self.suite.keywords.append(Keyword(name='Set service context to node_1', type='setup'))

        tests = [
            Keyword(name=u'Variable ABC: is ""'),
        ]
        with patch('modules.variable.exc.SetupError.ROBOT_EXIT_ON_FAILURE', False):
            run_keyword_tests(test_instance=self, setup=None, tests=tests, expected_result=Result.FAIL,
                              expected_message=u'ValidationError: Value')

