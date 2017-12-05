# coding=utf-8
import logging

from unittest2 import TestCase

from StringIO import StringIO
from robot.api import TestSuite

from Runtime import Runtime
from testutils import run_keyword_tests, Result


class TestRuntime(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runtime = Runtime()
        cls.stdout = StringIO()
        cls.settings = {'log_level': logging.DEBUG, 'output': None}

    def setUp(self):
        self.suite = TestSuite('Test Runtime Library')
        self.suite.resource.imports.library('Runtime')

    def tearDown(self):
        pass

    def test__e__pass(self):
        tests = [
            u' bla blub lba ',

        ]
        run_keyword_tests(test_instance=self, tests=tests, setup=None, expected_result=Result.PASS)

    def test__environment__pass(self):
        tests = [
            u'$HOME is set to ~/',
            u'$DOCKER_HOST is set to tcp://node2:6578/',
            u'$PATH contains /Applications/Wireshark.app/Contents/MacOS',

        ]
        run_keyword_tests(test_instance=self, tests=tests, setup=None, expected_result=Result.PASS)

    def test__environment__fail(self):
        tests = [
            u'$H OME is set to ~/',
            u'$DOCKER_HOST is set to I think tcp://node2:6578/',
            u'$PATH equals /Applications/Wireshark.app/Contents/MacOS'
            u'On nod e2, $DOCKER_HOST is set to tcp://node2:6578/'

        ]
        run_keyword_tests(test_instance=self, tests=tests, setup=None, expected_result=Result.FAIL)

    def test__environment_negation__pass(self):
        tests = [
            u'$HOME is not set to ~/',
            u'$DOCKER_HOST is not set to tcp://node2:6578/',
            u'$DOCKER_HOST does not contain tcp://node2:6578/',
            u'$PATH contains not /Applications/Wireshark.app/Contents/MacOS',
            u'On node2, $DOCKER_HOST is not set to tcp://node2:6578/'

        ]
        run_keyword_tests(test_instance=self, tests=tests, setup=None, expected_result=Result.PASS)

    def test__environment_with_context__pass(self):
        tests = [
            u'On node2 $DOCKER_HOST is set to tcp://node2:6578/',
            u'On node2, $DOCKER_HOST is set to tcp://node2:6578/',
            u'On 10.10.10.1, $DOCKER_HOST is set to tcp://node2:6578/',
            u'On node_3-2, $DOCKER_HOST is set to tcp://node2:6578/'

        ]
        run_keyword_tests(test_instance=self, tests=tests, setup=None, expected_result=Result.PASS)

    def test__environment_with_context__fail(self):
        tests = [
            u'On node2, DOCKER_HOST is set to tcp://node2:6578/',
            u'On no de2, $DOCKER_HOST is set to tcp://node2:6578/',
            u'On , $DOCKER_HOST is set to tcp://node2:6578/'

        ]
        run_keyword_tests(test_instance=self, tests=tests, setup=None, expected_result=Result.FAIL)

