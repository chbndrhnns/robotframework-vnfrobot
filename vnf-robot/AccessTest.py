import logging

from unittest2 import TestCase

from StringIO import StringIO
from robot.api import TestSuite

from Access import Access
from Network import Network
from testutils import run_keyword_tests, Result


class AccessNetwork(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stdout = StringIO()
        cls.settings = {'log_level': logging.DEBUG, 'output': None}

    def setUp(self):
        self.suite = TestSuite('Test Access Library')
        self.suite.resource.imports.library('Access')

    def tearDown(self):
        pass

    ###
    ### Tests for user objects
    ###

    def test__user_exists__pass(self):
        tests = [
            u'node1 has user "root"',
            u'"node1" has not user admin'
        ]
        run_keyword_tests(test_instance=self, setup=None, tests=tests, expected_result=Result.PASS)

    def test__user_exists__fail(self):
        tests = [
            u'"node1" has users "root"',
            u'node1 has not user adm in',
            u'node1 has user bla.1 with properties {"":}'
        ]

        run_keyword_tests(test_instance=self, setup=None, tests=tests, expected_result=Result.FAIL)

    def test__users_exists__pass(self):
        tests = [
            u'node1 has users ["root","admin"]',
            u'node1 has users ["root"]',
            u'node1 has users ["root",      "blub"]',
            u'"node1" has not users ["admin", "root"]'
        ]
        run_keyword_tests(test_instance=self, setup=None, tests=tests, expected_result=Result.PASS)

    def test__users_exists__fail(self):
        tests = [
            u'"node1" has user ["root"]',
            u'node1 has not users adm in',
            u'node1 has users bla.1 with properties {"":}'
            u'"node1" has not users [""]',
            u'"node1" has not users []'
        ]

        run_keyword_tests(test_instance=self, setup=None, tests=tests, expected_result=Result.FAIL)

    def test__user_has_properties__pass(self):
        tests = [
            u'node1 has user "root" with properties {"uid":"123", "gid":"5", "groups": ["root", "web"], "home":"/root", "shell":"/bin/bash"}',
            u'node1 has user "root" with properties {"uid":"123", "gid":"5", "groups": "root", "home":"/root", "shell":"/bin/bash"}',
            u'node1 has user "root" with properties {"uid":"123", "gid": 5, "groups": "root", "home":"/root", "shell":"/bin/bash"}',
            u'node1 has user root with properties {"uid":"123" }',
        ]
        run_keyword_tests(test_instance=self, setup=None, tests=tests, expected_result=Result.PASS)

    def test__user_has_properties__fail(self):
        tests = [
            u'node1 has users "root" with properties {"uid":"123", "gid":"5", "groups": ["root", "web"], "home":"/root", "shell":"/bin/bash"}',
            u'node1 has user "root" with properties {"uid":abc, "gid":"5", "groups": "root", "home":"/root", "shell":"/bin/bash"}',
            u'node1 has user "root" with properties {"uid":"123", }',
            u'node1 has user root with properties {:"123" }',
            u'node1 has user root with properties {"a": }',
        ]

        run_keyword_tests(test_instance=self, setup=None, tests=tests, expected_result=Result.FAIL)
        
    ###
    ### Tests for user objects
    ###

    def test__group_exists__pass(self):
        tests = [
            u'node1 has group "web"',
            u'"node1" has not group users'
        ]
        run_keyword_tests(test_instance=self, setup=None, tests=tests, expected_result=Result.PASS)

    def test__group_exists__fail(self):
        tests = [
            u'"node1" has groups "a"',
            u'node1 has not group this is a group',
            u'node1 has group bla.1 with properties {"":}'
        ]

        run_keyword_tests(test_instance=self, setup=None, tests=tests, expected_result=Result.FAIL)

    def test__groups_exists__pass(self):
        tests = [
            u'node1 has groups ["root","admin"]',
            u'node1 has groups ["root"]',
            u'node1 has groups ["root",      "blub"]',
            u'"node1" has not groups ["admin", "root"]'
        ]
        run_keyword_tests(test_instance=self, setup=None, tests=tests, expected_result=Result.PASS)

    def test__groups_exists__fail(self):
        tests = [
            u'"node1" has group ["root"]',
            u'node1 has not groups adm in',
            u'node1 has groups bla.1 with properties {"":}'
            u'"node1" has not groups [""]',
            u'"node1" has not groups []'
        ]

        run_keyword_tests(test_instance=self, setup=None, tests=tests, expected_result=Result.FAIL)

    def test__group_has_properties__pass(self):
        tests = [
            u'node1 has group "root" with properties {"gid":"123"}',
            u'node1 has group "root" with properties {"gid":123}',
            u'node1 has group root with properties {"gid":    "123"}',
        ]
        run_keyword_tests(test_instance=self, setup=None, tests=tests, expected_result=Result.PASS)

    def test__group_has_properties__fail(self):
        tests = [
            u'node1 has group root with properties',
            u'node1 has group root with properties {}',
            u'node1 has group root with properties {"a":"b"',
            u'node1 has group root with properties {"a""b"}',

        ]

        run_keyword_tests(test_instance=self, setup=None, tests=tests, expected_result=Result.FAIL)

