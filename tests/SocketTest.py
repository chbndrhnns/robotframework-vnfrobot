# -*- coding: utf-8 -*-
import socket
import unittest
from unittest import TestCase

from mock import patch

from Socket import Socket, NetcatServerWrapper
from exc import *

class SocketTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test__check_tcp_port__pass(self):
        # prepare
        port = 8080
        host = '127.0.0.1'
        sock = Socket()

        # do
        with NetcatServerWrapper((host, port)) as server:
            try:
                sock.check_tcp_port(host, port)
            except Exception as exc:
                self.fail('Not expected to fail with {}'.format(exc.__repr__()))

    @patch('Socket.socket.socket.connect')
    def test__check_tcp_port__port_closed__exception(self, mock_connect):
        # prepare
        port = 8991
        host = '127.0.0.2'
        sock = Socket()
        mock_connect.side_effect = socket.error('timed out')

        # do
        with self.assertRaises(TimeoutError):
            sock.check_tcp_port(host, port)

    def test__check_tcp_port__host_invalid__exception(self):
        # prepare
        port = 8991
        host = '1r27.0.0.2'
        sock = Socket()

        # do
        with self.assertRaisesRegexp(DataError, '[Errno 8]'):
            sock.check_tcp_port(host, port)

    def test__check_tcp_port__port_invalid__exception(self):
        # prepare
        port = 899100
        host = '127.0.0.2'
        sock = Socket()
        # mock_connect.side_effect = socket.error('timed out')

        # do
        with self.assertRaisesRegexp(DataError, 'not supported'):
            sock.check_tcp_port(host, port)


    @patch('Socket.socket.socket.connect')
    def test__check_tcp_port__dns__pass(self, mock_connect):
        # prepare
        port = 443
        host = 'www.telekom.de'
        sock = Socket()
        mock_connect.return_value = 0

        # do
        try:
            sock.check_tcp_port(host, port)
        except Exception as exc:
            self.fail('Not expected to fail with {}'.format(exc.__repr__()))
