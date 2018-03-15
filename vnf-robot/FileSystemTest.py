import logging

from unittest2 import TestCase

from StringIO import StringIO
from robot.api import TestSuite

from Network import Network
from testutils import run_keyword_tests, Result


class TestFilesystem(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.settings = {'log_level': logging.DEBUG, 'output': None}

    def setUp(self):
        self.suite = TestSuite('Test FileSystem Library')
        self.suite.resource.imports.library('FileSystem')

    def tearDown(self):
        pass

    ###
    ### Tests for file objects
    ###

    def test__object_exists__pass(self):
        tests = [
            u'"node1" has file /var/log/auth.log',
            u'"node1" has symlink /proc/cpu/cpuinfo',
            u'"node1" has no directory /proc/cpu/cpuinfo',
            u'"node1" has not directory /proc/cpu/cpuinfo',

        ]
        run_keyword_tests(test_instance=self, setup=None, tests=tests, expected_result=Result.PASS)

    def test__object_exists__fail(self):
        tests = [
            u'"node1" has no files /va r/log/auth.log',
            u'"node1" hasn\'t /proc/cpu/cpuinfo',
            u'"node1" has blub /proc/cpu/cpuinfo',
            u'"node1" has blub',
            u'"node1" has file',
        ]

        run_keyword_tests(test_instance=self, setup=None, tests=tests, expected_result=Result.FAIL)

    def test__objects_exist__pass(self):
        tests = [
            u'"node1" has files ["/var/log/auth.log"]',
            u'"node1" has files ["/var/log/auth.log", "/var/log/auth.log"]',
            u'"node1" has symlinks ["/proc/cpu/cpuinfo"]',
            u'"node1" has no directories ["/proc/cpu/cpuinfo"]',
            u'"node1" has not directories ["/proc/cpu/cpuinfo"]',

        ]
        run_keyword_tests(test_instance=self, setup=None, tests=tests, expected_result=Result.PASS)

    def test__objects_exist__fail(self):
        tests = [
            u'"node1" has files "/var/log/auth.log"',
            u'"node1" has file ["/var/log/auth.log"]',
            u'"node1" has files [""]',
            u'"node1" has directorys [""]',
            u'"node1" has directories [direc]',
            u'"node1" has directories []',
        ]

        run_keyword_tests(test_instance=self, setup=None, tests=tests, expected_result=Result.FAIL)
