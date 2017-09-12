# -*- coding: utf-8 -*-
import socket

from nclib import TCPServer

from settings import Settings
from exc import *
from robot.api import logger
from robot.api.deco import keyword
from robotlibcore import DynamicCore
from version import VERSION


class Socket(DynamicCore):
    """Socket is used to test for the status of TCP and UDP ports."""

    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'
    __version__ = VERSION

    def __init__(self):
        DynamicCore.__init__(self, [])

        logger.info("Importing {}".format(self.__class__))
        self.settings = Settings()

    def run_keyword(self, name, args, kwargs):
        """
        Mandatory method for using robot dynamic libraries

        Returns:
            None
        """
        logger.info("Running keyword '%s' with arguments %s." % (name, args))
        return self.keywords[name](*args, **kwargs)

    @keyword('${host}:${port}/TCP}')
    def check_tcp_port(self, host=None, port=None):
        """
        Issues an HTTP GET request to the specified url.

        Args:
            port: Port to be checked

        Returns:
            None

        """
        if port < 0 or port > 65535:
            raise DataError('Port "{}" is not supported.'.format(port))

        with SocketWrapper(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.connect((host, port))
            except socket.error as exc:
                if 'timed out' in exc.args:
                    raise TimeoutError()
                if exc.errno is 8:
                    raise DataError('Hostname not provided or invalid.')


class SocketWrapper:
    def __init__(self, family, t):
        self.family = family
        self.t = t

    def connect(self, bindto):
        self.sock.connect(bindto)

    def __enter__(self):
        self.sock = socket.socket(self.family, self.t)
        self.sock.settimeout(float(Settings().socket_timeout))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.sock.close()


class NetcatServerWrapper:
    def __init__(self, bindto):
        self.server = None
        self.bindto = bindto

    def __enter__(self):
        self.server = TCPServer(self.bindto)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.server.close()
