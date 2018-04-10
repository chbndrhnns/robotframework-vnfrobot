# -*- coding: utf-8 -*-
from robot.libraries.BuiltIn import BuiltIn

import exc
from robot.api import logger, TestSuite, TestData
from robot.api.deco import keyword

from Utils import Utils
from robotlibcore import DynamicCore
from version import VERSION


class Network(DynamicCore):
    """The Network module contains keywords to test for network configuration."""

    ROBOT_LIBRARY_SCOPE = 'TEST CASE'
    __version__ = VERSION

    def __init__(self):
        DynamicCore.__init__(self, [])
        self.context = None
        self.sut = None

        logger.info(u"Importing {}".format(self.__class__))

    def run_keyword(self, name, args, kwargs):
        """
        Mandatory method for using robot dynamic libraries

        Returns:
            None
        """
        self.context = BuiltIn().get_library_instance(all=True)

        logger.info(u"\nRunning keyword '%s' with arguments %s." % (name, args), also_console=True)
        return self.keywords[name](*args, **kwargs)

    @keyword('I can reach "${dst:\S+}"')
    def network_address_implicit_context(self, dst=None):
        """
        Validates that a destination is reachable from a node and fetches the context from the setup keywords.

        Args:
            dst: the address to test (IPv4, IPv6 or hostname)

        Returns:
            None

        """

        Utils.validate_argument(u'dst', dst)

    @keyword('I cannot reach "${dst:\S+}"')
    def network_address_negation_implicit_context(self, dst=None):
        """
        Validates that a destination is not reachable from a node and fetches the context from the setup keywords.

        Args:
            dst: the address to test (IPv4, IPv6 or hostname)

        Returns:
            None

        """

        Utils.validate_argument(u'dst', dst)

    @keyword('From "${src:\S+}"${delim:[,\s]*} I can reach "${dst:\S+}"')
    def network_address(self, src=None, delim=None, dst=None):
        """
        Validates that a destination is reachable from a node.

        Args:
            src: the node name of the node acting as the source of the test
            delim: used to catch different spelling variants
            dst: the address to test (IPv4, IPv6 or hostname)

        Returns:
            None

        """

        Utils.validate_argument(u'src', src)
        Utils.validate_argument(u'dst', dst)

    @keyword('From ${src:\S+}${trash:[,\s]*} I cannot reach ${dst:\S+}')
    def network_address_negation(self, src=None, trash=None, dst=None):
        """
        Validate that a destination is not reachable from a node.

        Args:
            src: the node name of the node acting as the source of the test
            dst: the address to test (IPv4, IPv6 or hostname)

        Returns:
            None

        """

        Utils.validate_argument(u'src', src)
        Utils.validate_argument(u'dst', dst)

    @keyword('From ${src:\S+}${trash:[,\s]*} "${fqdn:\S+}" ${operator:is|is only|is not} resolved to "${dst:\S+}"')
    def dns_resolve_single(self, src=None, trash=None, fqdn=None, operator='is', dst=None):
        """
        Validate that a FQDN resolves to a specified IP address.

        Args:
            fqdn: FQDN to resolve
            operator: is or is only is not
            trash: space or no space, ignored
            src: the node name of the node acting as the source of the test
            dst: the address to test (IPv4, IPv6 or hostname)

        Returns:
            None

        """

        self.dns_resolve_list(src, trash=None, fqdn=fqdn, operator=operator, dst='["{}"]'.format(dst))

    @keyword(
        'From ${src:\S+}${trash:[,\s]*} "${fqdn:\S+}" ${operator:is|is only|is not} resolved to ${dst:\[("\S+",?\s*)+\]}')
    def dns_resolve_list(self, src=None, trash=None, fqdn=None, operator='is', dst=None):
        """
        Validate that a FQDN resolves to a specified list of IP addresses.

        Args:
            fqdn: FQDN to resolve
            operator: is or is only or is not
            trash: space or no space, ignored
            src: the node name of the node acting as the source of the test
            dst: a list of IP addresses

        Returns:
            None

        """
        if dst is None:
            dst = []

        Utils.validate_argument(u'src', src)
        Utils.validate_argument(u'fqdn', fqdn)
        Utils.validate_argument(u'operator', operator)
        Utils.validate_list(u'dst', dst)

    @keyword(
        'From ${src:\S+}${trash:[,\s]*} lookup of "${fqdn:\S+}" ${operator:is|is not} successful')
    def dns_resolve_boolean(self, src=None, trash=None, fqdn=None, operator='is'):
        """
        Validate that a FQDN resolves to a specified list of IP addresses.

        Args:
            fqdn: FQDN to resolve
            operator: is or is only or is not
            trash: space or no space, ignored
            src: the node name of the node acting as the source of the test

        Returns:
            None

        """

        Utils.validate_argument(u'src', src)
        Utils.validate_argument(u'fqdn', fqdn)
        Utils.validate_argument(u'operator', operator)

    @keyword('${record:"[^"]+"} ${operator:is|is not} resolved')
    def dns_record(self, record=None, operator='is'):
        """
        Validate that a DNS record can be resolved.

        Args:
            record: DNS record ('<name> [<ttl>] IN <type> <rdata>')
            operator: is or is only or is not

        Returns:
            None

        """

        Utils.validate_string(u'record', record)
        Utils.validate_argument(u'operator', operator)

    @keyword(
        'On ${node:\S+}${trash:[,\s]*} ${interface:\S+} ${operator:has|has not} ${property:\S+}${comparator:\s*[=><!]{2\}\s*|\s*|\sof\s}${value:\S+}')
    def interface(self, node=None, trash=None, interface=None, operator='is', prop=None, comparator=None, value=None):
        """
        Validate that a network interface has a specified property

        Args:
            comparator: operation to perform on expected and actual value (==, !=, <=, >=)
            value: a value to match against an expected value
            prop: a property to validate
            interface: network interface name
            node: instance where the test is run
            operator: is or is only is not
            trash: space or no space, ignored

        Returns:
            None

        """

        Utils.validate_string(u'node', node)
        Utils.validate_string(u'interface', interface)
        Utils.validate_argument(u'operator', operator)
        Utils.validate_argument(u'prop', prop)
        if 'addresses' in prop.lower():
            Utils.validate_list(u'value', value)
        else:
            Utils.validate_argument(u'value', value)
        Utils.validate_argument(u'comparator', comparator.strip() or '==')

    @keyword(
        'On ${node:\S+}${trash:[,\s]*} ${interface:\S+} ${operator:has|has not} properties ${props:{[^\}]+\}}')
    def interface_property_dict(self, node=None, trash=None, interface=None, operator='is', props=None):
        """
        Validate that a network interface has properties as given in a JSON dictionary

        Args:
            props: a property to validate
            interface: network interface name
            node: instance where the test is run
            operator: is or is only is not
            trash: space or no space, ignored

        Returns:
            None

        """

        Utils.validate_string(u'node', node)
        Utils.validate_string(u'interface', interface)
        Utils.validate_argument(u'operator', operator)
        Utils.validate_json(u'props', props)

    @keyword(
        'On ${node:\S+}${trash:[,\s]*} ${interface:\S+} ${operator:is|is not} active')
    def interface_active(self, node=None, trash=None, interface=None, operator='is'):
        """
        Validate that a network interface has a specified address

        Args:
            interface: network interface name
            node: instance where the test is run
            operator: is or is only is not
            trash: space or no space, ignored

        Returns:
            None

        """

        Utils.validate_string(u'node', node)
        Utils.validate_string(u'interface', interface)
        Utils.validate_argument(u'operator', operator)

    @keyword(
        'On ${node:\S+}${trash:[,\s]*} ${interface:\S+} ${operator:has no[^t]} ${prop:\S+}')
    def interface_has_no(self, node=None, trash=None, interface=None, operator='is', prop=None):
        """
        Validate that a network interface has no assigned address

        Args:
            prop: property to check
            interface: network interface name
            node: instance where the test is run
            operator: is or is only is not
            trash: space or no space, ignored

        Returns:
            None

        """

        Utils.validate_string(u'node', node)
        Utils.validate_string(u'interface', interface)
        Utils.validate_argument(u'operator', operator)
        Utils.validate_argument(u'prop', prop)

    # @keyword(
    #     'On ${node:\S+}${trash:[,\s]*} ${interface:\S+} ${operator:has|has not} ${numerus:address|addresses} ${addresses:\s+\[('
    #     '"\S+",?\s*)+\]}')
    # def interface_has_addresses(self, node=None, trash=None, interface=None, operator='has', numerus='address', addresses='None'):
    #     """
    #     Validate that a network interface has a specified address
    #
    #     Args:
    #         numerus: address or addresses
    #         addresses: address to validate
    #         interface: network interface name
    #         node: instance where the test is run
    #         operator: is or is only is not
    #         trash: space or no space, ignored
    #
    #     Returns:
    #         None
    #
    #     """
    #
    #
    #     # if addresses is None:
    #     #     addresses = []
    #     # if not isinstance(addresses, list):
    #     #     addresses = list(addresses)
    #
    #     Utils.validate_string(u'node', node)
    #     Utils.validate_string(u'interface', interface)
    #     Utils.validate_argument(u'operator', operator)
    #     if 'addresses' in numerus.lower():
    #         Utils.validate_list(u'addresses', addresses)
    #     else:
    #         Utils.validate_argument(u'address', addresses)

    @keyword(
        'On ${node:\S+}${trash:[,\s]*} port ${port:\d+|\d+/tcp|\d+/udp} is ${operator:open|closed}')
    def port_is(self, node=None, trash=None, port=None, status='open'):
        """
        Validate that a port is either open or closed

        Args:
            port: network port number
            node: instance where the test is run
            status: open or closed
            trash: space or no space, ignored

        Returns:
            None

        """

        Utils.validate_string(u'node', node)
        Utils.validate_string(u'port', port)
        Utils.validate_string(u'status', status)

    @keyword(
        'On ${node:\S+}${trash:[,\s]*} ports ${ports:\[("\S+",?\s*)+\]} are ${operator:open|closed}')
    def ports_list(self, node=None, trash=None, ports=None, status='open'):
        """
        Validate that a port is either open or closed

        Args:
            ports: list of network port number
            node: instance where the test is run
            status: open or closed
            trash: space or no space, ignored

        Returns:
            None

        """

        Utils.validate_string(u'node', node)
        Utils.validate_list(u'ports', ports)
        Utils.validate_string(u'status', status)

    @keyword(
        'On ${node:\S+}${trash:[,\s]*}${port_type:udp|TCP|\s*} ports ${port_start:\d+} to ${port_end:\d+} are ${operator:open|closed}')
    def ports_range(self, node=None, trash=None, port_type='tcp', port_start=None, port_end='None', status='open'):
        """
        Validate that a range of ports is either open or closed

        Args:
            port_type: tcp or udp
            port_end: end of port range
            port_start: start of port range
            node: instance where the test is run
            status: open or closed
            trash: space or no space, ignored

        Returns:
            None

        """

        # TODO: change style to match other port definitions: 22/tcp

        Utils.validate_string(u'node', node)
        Utils.validate_string(u'port_type', port_type or 'tcp')
        Utils.validate_string(u'port_start', port_start)
        Utils.validate_string(u'port_end', port_end)
        Utils.validate_string(u'status', status)

    def _get_context(self):
        s = TestSuite()
        d = TestData()
        logger.info('')