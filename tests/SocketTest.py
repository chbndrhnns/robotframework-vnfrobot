# -*- coding: utf-8 -*-
import socket
import unittest
from unittest import TestCase

from mock import patch

from Socket import Socket, NetcatTcpServerWrapper, NetcatUdpServerWrapper
from exc import *


class SocketTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test__check_port__tcp_pass(self):
        # prepare
        port = 8080
        host = '127.0.0.1'
        sock = Socket()

        # do
        with NetcatTcpServerWrapper((host, port)) as server:
            try:
                sock.check_port(host, port)
            except Exception as exc:
                self.fail(u'Not expected to fail with {}'.format(exc.__repr__()))

    def test__check_port__string_port__pass(self):
        # prepare
        port = '8080'
        host = '127.0.0.1'
        sock = Socket()

        # do
        with NetcatTcpServerWrapper((host, int(port))) as server:
            try:
                sock.check_port(host, port)
            except Exception as exc:
                self.fail(u'Not expected to fail with {}'.format(exc.__repr__()))

    def test__check_port__unicode_port__pass(self):
        # prepare
        port = u'8080'
        host = '127.0.0.1'
        sock = Socket()

        # do
        with NetcatTcpServerWrapper((host, int(port))) as server:
            try:
                sock.check_port(host, port)
            except Exception as exc:
                self.fail(u'Not expected to fail with {}'.format(exc.__repr__()))

    def test__check_port__udp__pass(self):
        # prepare
        port = 8080
        host = '127.0.0.1'
        sock = Socket()

        # do
        with NetcatUdpServerWrapper((host, port)) as server:
            try:
                sock.check_port(host, port)
            except Exception as exc:
                self.fail(u'Not expected to fail with {}'.format(exc.__repr__()))

    @patch('Socket.socket.socket.connect')
    def test__check_port__tcp_port_closed__exception(self, mock_connect):
        # prepare
        port = 8991
        host = '127.0.0.2'
        sock = Socket()
        mock_connect.side_effect = socket.error('timed out')

        # do
        with self.assertRaises(TimeoutError):
            sock.check_port(host, port)

    def test__check_port__tcp_host_invalid__exception(self):
        # prepare
        port = 8991
        host = '1r27.0.0.2'
        sock = Socket()

        # do
        with self.assertRaisesRegexp(DataError, u'Cannot parse host'):
            sock.check_port(host, port)

    def test__check_port__tcp_port_invalid__exception(self):
        # prepare
        port = 899100
        host = '127.0.0.2'
        sock = Socket()

        # do
        with self.assertRaisesRegexp(DataError, u'be in range'):
            sock.check_port(host, port)

    def test__check_port__tcp_None_port__exception(self):
        # prepare
        port = None
        host = '127.0.0.2'
        sock = Socket()

        # do
        with self.assertRaisesRegexp(DataError, u'not supported'):
            sock.check_port(host, port)

    def test__check_port__tcp_None_host__exception(self):
        # prepare
        port = 80
        host = None
        sock = Socket()

        # do
        with self.assertRaisesRegexp(DataError, u'Cannot parse host'):
            sock.check_port(host, port)

    @patch('Socket.socket.socket.connect')
    def test__check_port__tcp_dns__pass(self, mock_connect):
        # prepare
        port = 443
        host = u'www.telekom.de'
        sock = Socket()
        mock_connect.return_value = 0

        # do
        try:
            sock.check_port(host, port)
        except Exception as exc:
            self.fail(u'Not expected to fail with {}'.format(exc.__repr__()))

    def test__check_port__tcp_ipv6__pass(self):
        # prepare
        port = 80
        host = u'::1'
        sock = Socket()

        # do
        try:
            sock.check_port(host, port)
        except Exception as exc:
            self.fail(u'Not expected to fail with {}'.format(exc.__repr__()))

    def test__check_port__udp_ipv6__pass(self):
        # prepare
        port = 443
        host = '::222'
        protocol = u'udp'
        sock = Socket()

        # do
        with NetcatUdpServerWrapper((host, port)) as server:
            try:
                sock.check_port(host, port, protocol)
            except Exception as exc:
                self.fail(u'Not expected to fail with {}'.format(exc.__repr__()))

    def test__check_port__protocol_invalid__exception(self):
        # prepare
        port = 443
        host = u'::1'
        protocol = u'uap'
        sock = Socket()

        # do
        with self.assertRaisesRegexp(DataError, u'UDP and TCP'):
            sock.check_port(host, port, protocol)



