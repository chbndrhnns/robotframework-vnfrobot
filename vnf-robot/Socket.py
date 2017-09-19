# -*- coding: utf-8 -*-
import socket
from string import lower

import ipaddress
import pydevd
from nclib import TCPServer, UDPServer

from settings import Settings
from exc import *
from robot.api import logger
from robot.api.deco import keyword
from robotlibcore import DynamicCore
from version import VERSION

HTTP_PORT = 80


class Layer4Port:
    def __init__(self, port):
        if port is None:
            raise DataFormatError(u'None port is not supported.'.format(port))
        try:
            self.port = int(port)
        except ValueError:
            raise DataFormatError(u'Non-numerical port is not supported.'.format(port))

        if self.port < 0 or self.port > 65535:
            raise DataFormatError(u'Port must be in range "0 <= port <= 65535". Got "{}"'.format(port))


class Layer3Protocol:
    allowed = {
        u'udp': socket.SOCK_DGRAM,
        u'tcp': socket.SOCK_STREAM
    }

    def __init__(self, protocol):
        error = None

        if protocol is None:
            error = DataFormatError(u'Only UDP and TCP are support protocols; got None.'.format(protocol))
        self.type = self.allowed.get(unicode.lower(protocol), None)
        if self.type is None:
            error = DataFormatError(u'Only UDP and TCP are support protocols; got "{}".'.format(protocol))

        if error is not None:
            raise error


class HostAddress:
    def __init__(self, address=None):
        if address is None:
            raise DataError(u'Cannot parse host None')

        error = None
        try:
            self.host_address = ipaddress.ip_address(address)
        except ValueError as exc:
            error = DataFormatError(u'Cannot parse host "{}"'.format(address))

        try:
            error = None
            self.host_address = socket.getaddrinfo(address, HTTP_PORT)
        except socket.gaierror as exc:
            error = DataFormatError(u'Cannot parse host "{}"'.format(address))

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


class NetcatTcpServerWrapper:
    def __init__(self, bindto):
        self.server = None
        self.bindto = bindto

    def __enter__(self):
        self.server = TCPServer(self.bindto)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.server.close()


class NetcatUdpServerWrapper:
    def __init__(self, bindto):
        self.server = None
        self.bindto = bindto

    def __enter__(self):
        self.server = UDPServer(self.bindto)

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

    @keyword('${host}:${port:\d+}/${protocol}')
    def check_port(self, host=None, port=None, protocol='TCP'):
        """
        Check whether a port is open on the specified host.

        Args:
            host: host or domain name
            protocol: TCP or UDP
            port: Port to be checked

        Returns:
            None

        """
        # verify protocol
        proto = Layer3Protocol(unicode(protocol)).type

        # verify port
        l4port = Layer4Port(unicode(port)).port

        # verify host
        address_family = HostAddress(unicode(host)).version

        with SocketWrapper(address_family, proto) as sock:
            try:
                logger.info(u'Establishing connection to {}:{}/{}'.format(host, l4port, protocol))
                # pydevd.settrace('localhost', port=65000, stdoutToServer=True, stderrToServer=True)

                sock.connect((host, l4port))
            except socket.error as exc:
                if 'Connection refused' in exc.args:
                    raise ConnectionError('Connection refused for {}:{}/{}'.format(host, l4port, protocol))
                if 'timed out' in exc.args:
                    raise TimeoutError('Timeout for {}:{}/{}'.format(host, l4port, protocol))
