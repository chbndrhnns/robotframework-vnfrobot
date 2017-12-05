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

    ###
    ### Module Environment
    ###

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

    ###
    ### Module Command
    ###

    def test__command__pass(self):
        tests = [
            u'Command "bash -c ps aux" exits with status 0',
            u'Command "apt info htop" exits with status "255"'
        ]
        run_keyword_tests(test_instance=self, tests=tests, setup=None, expected_result=Result.PASS)

    def test__command_with_stream__pass(self):
        tests = [
            u'Command "apt info htop" exits with status 0 and stdout contains "Installed"',
            u'Command "apt install gcc-notexistant" exits with status 1 and stderr contains "not found"',
            u'Command "echo $(ls -l -1)" exits with status 0 and stdout contains "bin"',

        ]
        run_keyword_tests(test_instance=self, tests=tests, setup=None, expected_result=Result.PASS)

    def test__command__fail(self):
        tests = [
            u'Command bash -c ps aux exits with status 0',
            u'Command "bash -c ps aux exits with status 0',
            u'Command "bash -c ps aux exits with status "0',
            u'Command "bash -c ps aux" exits with status a',
            u'Command "bash -c ps aux" exits with status 1234',
            u'Command "bash -c ps aux" exits with status 1234',

        ]
        run_keyword_tests(test_instance=self, tests=tests, setup=None, expected_result=Result.FAIL)

    def test__command_with_stream__fail(self):
        tests = [
            u'Command "apt info htop" exits with status 0 and stdout contains ""',
            u'Command "apt info htop" exits with status 0 and stdout contains bla',
        ]
        run_keyword_tests(test_instance=self, tests=tests, setup=None, expected_result=Result.FAIL)

    ###
    ### Module Process
    ###

    def test__process__pass(self):
        tests = [
            u'Process "java -jar bla.jar" is running',
            u'Process nginx is running',

        ]
        run_keyword_tests(test_instance=self, tests=tests, setup=None, expected_result=Result.PASS)

    def test__process__fail(self):
        tests = [
            u'Process java -jar bla.jar is running',
            u'Process java -jar bla.jar is not running',
            u'Process \'nginx\' runs',
            u'Process nginx runs',

        ]
        run_keyword_tests(test_instance=self, tests=tests, setup=None, expected_result=Result.FAIL)

    def test__process_negation__pass(self):
        tests = [
            u'Process "java -jar bla.jar" is not running',
            u'Process nginx is not running',

        ]
        run_keyword_tests(test_instance=self, tests=tests, setup=None, expected_result=Result.PASS)

    ###
    ### Module Service
    ###

    def test__service__pass(self):
        tests = [
            u'Service "apache2" is running',
            u'Service gitlab-ce is running',

        ]
        run_keyword_tests(test_instance=self, tests=tests, setup=None, expected_result=Result.PASS)

    def test__service__fail(self):
        tests = [
            u'Service gitlab ce is running',
            u'Service 123 ce is not running',
        ]
        run_keyword_tests(test_instance=self, tests=tests, setup=None, expected_result=Result.FAIL)

    def test__service_negation__pass(self):
        tests = [
            u'Service "apache2" is not running',
            u'Service gitlab-ce is not running',
        ]
        run_keyword_tests(test_instance=self, tests=tests, setup=None, expected_result=Result.PASS)


