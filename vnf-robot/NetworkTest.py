import logging

from unittest2 import TestCase

from StringIO import StringIO
from robot.api import TestSuite

from Network import Network
from testutils import run_keyword_tests, Result


class TestNetwork(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.network = Network()
        cls.stdout = StringIO()
        cls.settings = {'log_level': logging.DEBUG, 'output': None}

    def setUp(self):
        self.suite = TestSuite('Test Network Library')
        self.suite.resource.imports.library('Network')

    def tearDown(self):
        pass

    def test__network_address__pass(self):
        tests = [
            u'From "node1", I can reach "10.10.10.1"',
            u'From "dns-daemon", I can reach "fe80::62f1:eadc:86a0:c33d"',
            u'From "master" I can reach "mqrabbit.staging.local"',

        ]
        run_keyword_tests(test_instance=self, setup=None, tests=tests, expected_result=Result.PASS)

    def test__network_address__fail(self):
        tests = [
            u'From "a", I can reach ""',
            u'From "", I can reach "b"',
            u'From "a b", I can reach "a b"'
        ]

        run_keyword_tests(test_instance=self, setup=None, tests=tests, expected_result=Result.FAIL)

    def test__network_address_negation__pass(self):
        tests = [
            u'From node1, I cannot reach 10.10.10.1',
            u'From dns-daemon, I cannot reach fe80::62f1:eadc:86a0:c33d',
            u'From master, I cannot reach mqrabbit.staging.local',
        ]

        run_keyword_tests(test_instance=self, setup=None, tests=tests, expected_result=Result.PASS)

    def test__network_address_negation__fail(self):
        tests = [
            u'From a b, I cannot reach bla',
            u'From "a, I cannot reach',
            u'From a b, I cannot reach a b'
        ]

        run_keyword_tests(test_instance=self, setup=None, tests=tests, expected_result=Result.FAIL)

    def test__network_address_implicit_context__pass(self):
        tests = [
            u'I can reach "10.10.10.1"',
            u'I can reach "fe80::62f1:eadc:86a0:c33d"',
            u'I can reach "mqrabbit.staging.local"',

        ]
        run_keyword_tests(test_instance=self, setup=None, tests=tests, expected_result=Result.PASS)
