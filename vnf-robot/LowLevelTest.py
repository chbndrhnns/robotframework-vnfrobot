import logging
from StringIO import StringIO
from mock import patch

from unittest2 import TestCase

from robot.api import TestSuite
from robot.running import Keyword
from testutils import run_keyword_tests, Result


class LowLevelTest(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.settings = {'log_level': logging.DEBUG, 'output': None, 'stdout': StringIO()}

    def setUp(self):
        self.suite = TestSuite('Test low level keywords')
        self.suite.resource.imports.library('LowLevel')

    def tearDown(self):
        pass

    def test__env_vars__no_target__fail(self):
        tests = [
            Keyword(name=u'Get Environment Variables'),
            Keyword(name=u'Execute Command'),
            Keyword(name=u'Get Process'),
            Keyword(name=u'Get Service'),
            Keyword(name=u'Get Kernel Parameters'),
            Keyword(name=u'Inspect Container'),
            Keyword(name=u'Check User'),
            Keyword(name=u'Check Group'),
            Keyword(name=u'Check File'),
            Keyword(name=u'Check Symbolic link'),
            Keyword(name=u'Check Address'),
            Keyword(name=u'Resolve DNS Record'),
            Keyword(name=u'Check Interface'),
            Keyword(name=u'Check Port'),
        ]
        with patch('LowLevel.exc.SetupError.ROBOT_EXIT_ON_FAILURE', False):
            run_keyword_tests(test_instance=self, setup=None, tests=tests, expected_result=Result.FAIL, expected_message=u'SetupError: Target type')

    def test__env_vars__node_target__pass(self):
        self.suite.keywords.append(Keyword(name='Set Target', args=['node', 'flamboyant_saha'], type='setup'))

        tests = [
            Keyword(name=u'Get Environment Variables'),
            Keyword(name=u'Execute Command'),
            Keyword(name=u'Get Process'),
            Keyword(name=u'Get Service'),
            Keyword(name=u'Get Kernel Parameters'),
            Keyword(name=u'Inspect Container'),
            Keyword(name=u'Check User'),
            Keyword(name=u'Check Group'),
            Keyword(name=u'Check File'),
            Keyword(name=u'Check Symbolic link'),
            Keyword(name=u'Check Address'),
            Keyword(name=u'Resolve DNS Record'),
            Keyword(name=u'Check Interface'),
            Keyword(name=u'Check Port'),

        ]

        run_keyword_tests(test_instance=self, tests=tests, expected_result=Result.PASS)

