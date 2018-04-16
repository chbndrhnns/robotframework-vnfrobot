import logging
from mock import patch, MagicMock

from unittest2 import TestCase

from robot.api import TestSuite
from robot.running import Keyword

from DockerController import DockerController
from tools.testutils import run_keyword_tests, Result


class VariableTest(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.settings = {'log_level': logging.DEBUG}

    def setUp(self):
        self.suite = TestSuite('Test low level keywords')
        self.suite.resource.imports.library('LowLevel')

    def tearDown(self):
        pass

    def test__variable__invalid_var__fail(self):
        self.suite.keywords.append(Keyword(name='Set service context to node_1', type='setup'))

        tests = [
            Keyword(name=u'Variable 80: is b'),
            Keyword(name=u'Variable abc: is b'),
            Keyword(name=u'Variable A-B: is b'),
        ]
        # with patch('modules.variable.exc.SetupError.ROBOT_EXIT_ON_FAILURE', False):
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

        with patch('LowLevel.orchestrator._get_controller') as mock:
            mock.return_value = MagicMock(DockerController)
            mock.return_value.get_env.return_value = ["PATH=/usr/bin", "NGINX_VERSION=2.0.0beta1"]
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
