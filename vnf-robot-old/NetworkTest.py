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

    ###
    ### Tests for network address
    ###

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

    ###
    ### Tests for dns resolution
    ###

    def test__dns_resolve_single__pass(self):
        tests = [
            u'From node-1, "www.google.de" is resolved to "8.8.8.8"',
            u'From node-1, "www.google.de" is only resolved to "8.8.8.8"',
            u'From node-1, "www.google.de" is not resolved to "9.9.9.9"',

        ]
        run_keyword_tests(test_instance=self, setup=None, tests=tests, expected_result=Result.PASS)

    def test__dns_resolve_single__fail(self):
        tests = [
            u'From node-1, www.google.de" is resolved to "8.8.8.8"',
            u'From node-1, www.google.de is resolved to "8.8.8.8"',
            u'From node-1, "www.google.de" is resolved to 9.9.9.9',
            u'From nod e-1, "www.google.de" is resolved to 9.9.9.9',
            u'From node-1, "www.google.de" is resolves to "9.9.9.9"',

        ]
        run_keyword_tests(test_instance=self, setup=None, tests=tests, expected_result=Result.FAIL)

    def test__dns_resolve_list__pass(self):
        tests = [
            u'From node-1, "www.google.de" is resolved to ["8.8.8.8", "127.127.127.127"]',
            u'From node-1, "www.google.de" is only resolved to ["8.8.8.8", "127.127.127.127"]',
            u'From node-1, "www.google.de" is not resolved to ["9.9.9.9","127.0.0.1"]',
            u'From node-1, "www.google.de" is not resolved to ["9.9.9.9",  "127.0.0.1"]',
        ]
        run_keyword_tests(test_instance=self, setup=None, tests=tests, expected_result=Result.PASS)

    def test__dns_resolve_list__fail(self):
        tests = [
            u'From node-1, "www.google.de" is resolved to [8.8.8.8", "127.127.127.127"]',
            u'From node-1, "www.google.de" is not resolved to ["9.9.9.9", "127.0.0.1"',
        ]
        run_keyword_tests(test_instance=self, setup=None, tests=tests, expected_result=Result.FAIL)

    def test__dns_record__pass(self):
        tests = [
            u'"test.example.com. 3600 IN A  172.30.0.7" is resolved',
            u'"7.0.30.172.in-addr.arpa.           PTR     test.example.com." is resolved',
        ]
        run_keyword_tests(test_instance=self, setup=None, tests=tests, expected_result=Result.PASS)

    def test__dns_record__fail(self):
        tests = [
            u'"7.0.30.172.in-addr.arpa.           PTR     test.example.com. is resolved',
        ]
        run_keyword_tests(test_instance=self, setup=None, tests=tests, expected_result=Result.FAIL)

    def test__dns_resolve_boolean__pass(self):
        tests = [
            u'From node-1, lookup of "www.google.de" is successful',
            u'From node-1, lookup of "www.google.de" is not successful',
        ]
        run_keyword_tests(test_instance=self, setup=None, tests=tests, expected_result=Result.PASS)

    def test__dns_resolve_boolean__fail(self):
        tests = [
            u'From node-1, lookup of "www.google.de is successful',
            u'From node-1, lookup of "" is not successful',
        ]
        run_keyword_tests(test_instance=self, setup=None, tests=tests, expected_result=Result.FAIL)

    ###
    ### Tests for network interface properties
    ###

    def test__interface__pass(self):
        tests = [
            u'On node1, eth0 has mtu_size of 1500',
            u'On node1, "vlan1.1230" has mac_address ab:cd:ef:gh',
            u'On node1, vlan1.1230 has mac_address ab:cd:ef:gh',
            u'On node1, vlan1.1230 is active',
            u'On node1, vlan1.1230 is not active',
            u'On node1, vlan1.1230 has address 123.7.0.1',
            u'On node1, vlan1.1230 has address "123.7.0.1"',
            u'On node1, vlan1.1230 has address ["123.7.0.1"]',
            u'On node1, vlan1.1230 has not address 123.7.0.1/32',
            u'On node1, vlan1.1230 has properties { "addresses": ["123.7.0.1/32", "125.1.1.5"]}',
            u'On node1, vlan1.1230 has no address',
            u'On node1, eth0 has mtu_size >= 1500',
            u'On node1, eth0 has mtu_size != 1500',
            u'On node1, eth0 has mtu_size <= 1500',
            u'On node1, eth0 has mtu_size == 1500',
            u'On node1, eth0 has mtu_size==1500',
        ]
        run_keyword_tests(test_instance=self, setup=None, tests=tests, expected_result=Result.PASS)

    def test__interface__fail(self):
        tests = [
            u'On node1, eth0 has mtu_ size U 1500',
            u'On node1, eth 0 has MT U 1500',
            u'On node1, vlan1.1230 is actived',
            u'On node1, vlan1.1230 has addresses ["123.7.0.1/32"',
            u'On node1, vlan1.1230 has addresses "123.7.0.1/32"',
            u'On node1, vlan1.1230 has addresses ["123.7.0.1/32" "125.1.1.5"]',
            u'On node1, vlan1.1230 has no address 127.0.0.1',
            u'On node1, eth0 has mtu_size = 1500',
        ]
        run_keyword_tests(test_instance=self, setup=None, tests=tests, expected_result=Result.FAIL)

    ###
    ### Tests for network port properties
    ###

    def test__port__pass(self):
        tests = [
            u'On node1, port 22 is open',
            u'On node1, port 22 is closed',
            u'On node1, port 22/TCP is closed',
            u'On node1, port 22/tcp is closed',
            u'On node1, port 22/UDP is closed',
            u'On node1, port 65535 is closed',
            u'On node1, ports ["22/tcp", "23/udp"] are open',
            u'On node1, ports ["65/tcp", "443"] are closed',
            u'On node1, ports 5000 to 5005 are closed',
            u'On node1, ports 5000 to 5005 are open',
            u'On node1, UDP ports 5000 to 5005 are open',

        ]

        run_keyword_tests(test_instance=self, setup=None, tests=tests, expected_result=Result.PASS)

    def test__port__fail(self):
        tests = [
            u'On node1, port 2d2 is open',
            u'On node1, port 22 is close',
            u'On node1, port 22/abs is closed',
            u'On node1, port 22:udp is closed',
            u'On node1, port 655.353 is closed',
            u'On node1, ports ["22/tcp", "23/udp"] is open',
            u'On node1, port ["65/tcp", "443"] are closed',
            u'On node1, udp port 5000 to 5005 are closed',

        ]

        run_keyword_tests(test_instance=self, setup=None, tests=tests, expected_result=Result.FAIL)
