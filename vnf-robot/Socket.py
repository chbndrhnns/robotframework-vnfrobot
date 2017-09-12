# -*- coding: utf-8 -*-
import socket
from string import lower

import ipaddress
from nclib import TCPServer

from settings import Settings
from exc import *
from robot.api import logger
from robot.api.deco import keyword
from robotlibcore import DynamicCore
from version import VERSION


class Layer3Protocol:
    allowed = {
        'udp': socket.SOCK_DGRAM,
        'tcp': socket.SOCK_STREAM
    }

    def __init__(self, protocol):
        if protocol is None:
            raise DataError('Only UDP and TCP are support protocols; got None.'.format([protocol]))
        self.type = self.allowed.get(str.lower(protocol), None)
        if self.type is None:
            raise DataError('Only UDP and TCP are support protocols; got "".'.format([protocol]))


class HostAddress:
    def __init__(self, address=None):
        error = None
        try:
            self.host_address = ipaddress.ip_address(address)
        except ipaddress.AddressValueError as exc:
            error = DataError('Cannot parse provided host "{}"'.format(address))

        try:
            error = None
            self.host_address = socket.getaddrinfo(address, 80)
        except socket.gaierror as exc:
            error = DataError('Cannot parse provided host "{}"'.format(address))

        if error is not None:
            raise error

    @property
    def version(self):
        return [family[0] for family in self.host_address][0]


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

    @keyword('${host}:${port}/${protocol}}')
    def check_port(self, host=None, port=None, protocol='TCP'):
        """
        Issues an HTTP GET request to the specified url.

        Args:
            host: host or domain name
            protocol: TCP or UDP
            port: Port to be checked

        Returns:
            None

        """

        # verify port
        if port is None:
            raise DataError('None port is not supported.'.format(port))
        if port < 0 or port > 65535:
            raise DataError('Port "{}" is not supported.'.format(port))

        # verify host
        address_family = HostAddress(host).version

        # verify protocol
        proto = Layer3Protocol(protocol).type

        with SocketWrapper(address_family, proto) as sock:
            try:
                sock.connect((host, port))
            except socket.error as exc:
                if 'timed out' in exc.args:
                    raise TimeoutError()
                if exc.errno is 8:
                    raise DataError('Hostname not provided or invalid.')
