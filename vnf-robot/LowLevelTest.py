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
            Keyword(name=u'Environment Variable'),
            Keyword(name=u'Command'),
            Keyword(name=u'Process'),
            Keyword(name=u'Service'),
            Keyword(name=u'Kernel Parameter'),
            Keyword(name=u'Container'),
            Keyword(name=u'User'),
            Keyword(name=u'Group'),
            Keyword(name=u'File'),
            Keyword(name=u'Symbolic link'),
            Keyword(name=u'Address'),
            Keyword(name=u'DNS'),
            Keyword(name=u'Interface'),
            Keyword(name=u'Port'),
        ]
        with patch('LowLevel.exc.SetupError.ROBOT_EXIT_ON_FAILURE', False):
            run_keyword_tests(test_instance=self, setup=None, tests=tests, expected_result=Result.FAIL, expected_message=u'SetupError: Target type')

    def test__env_vars__node_target__pass(self):
        self.suite.keywords.append(Keyword(name='Set Target', args=['node', 'flamboyant_saha'], type='setup'))

        tests = [
            Keyword(name=u'Environment Variable'),
            Keyword(name=u'Command'),
            Keyword(name=u'Process'),
            Keyword(name=u'Service'),
            Keyword(name=u'Kernel Parameter'),
            Keyword(name=u'Container'),
            Keyword(name=u'User'),
            Keyword(name=u'Group'),
            Keyword(name=u'File'),
            Keyword(name=u'Symbolic link'),
            Keyword(name=u'Address'),
            Keyword(name=u'DNS'),
            Keyword(name=u'Interface'),
            Keyword(name=u'Port'),
        ]

        run_keyword_tests(test_instance=self, tests=tests, expected_result=Result.PASS)

