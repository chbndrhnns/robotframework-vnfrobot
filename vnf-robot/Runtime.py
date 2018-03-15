# -*- coding: utf-8 -*-
from robot.libraries.BuiltIn import BuiltIn

import exc
from robot.api import logger, TestSuite, TestData
from robot.running import context
from robot.api.deco import keyword

from Utils import Utils
from robotlibcore import DynamicCore
from version import VERSION


class Runtime(DynamicCore):
    """The Runtime module contains keywords to test for runtime configuration."""

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

    @keyword('On ${host:[^\s,]+}${delim:[,\s]*}${variable:\$\w+} ${operator:is set to|contains} ${value:\S+}')
    def environment_with_context(self, host=None, delim=None, *args):
        """
        Validates that an environment variable is set on a specific host.
        The host name is implicitly derived from a setup variable.

        Args:
            delim: optional comma delimiter
            host: the system under test
            variable: an environment variable name
            val: the value of the variable
            operator: the validation operation to perform

        Returns:
            None

        """

        self.environment(*args)

    @keyword('On ${host:[^\s,]+}${delim:[,\s]*}${variable:\$\w+} ${operator:is not set to|contains not|does not contain} ${value:\S+}')
    def environment_with_context_negation(self, host=None, delim=None, *args):
        """
        Validates that an environment variable is set on a specific host.
        The host name is implicitly derived from a setup variable.

        Args:
            delim: optional comma delimiter
            host: the system under test
            variable: an environment variable name
            val: the value of the variable
            operator: the validation operation to perform

        Returns:
            None

        """

        self.environment(*args)

    @keyword('${variable:^\$\w+} ${operator:(is set to|contains)} ${value:\S+}')
    def environment(self, variable=None, operator=None, val=None):
        """
        Validates that an environment variable is set on a specific host.
        The host name is implicitly derived from a setup variable.

        Args:
            variable: an environment variable name
            val: the value of the variable
            operator: the validation operation to perform

        Returns:
            None

        """

        Utils.validate_argument(u'src', variable)
        Utils.validate_argument(u'operator', operator)
        Utils.validate_argument(u'value', val)

    @keyword('${variable:^\$\w+} ${operator:(is not set to|does not contain|contains not)} ${value:\S+}')
    def environment_negation(self, variable=None, operator=None, val=None):
        """
        Validates that an environment variable is not set on a specific host.
        The host name is implicitly derived from a setup variable.

        Args:
            variable: an environment variable name
            val: the value of the variable
            operator: the validation operation to perform

        Returns:
            None

        """

        Utils.validate_argument(u'src', variable)
        Utils.validate_argument(u'operator', operator)
        Utils.validate_argument(u'value', val)

    @keyword('Command ${cmd:".+"} exits with status ${exit_status:([0-9]{1,3\})|("[0-9]{1,3\}")}')
    def command(self, cmd=None, exit_status=None):
        """
        Validates that a command gets executed  on a specific host and verifies the return code is as expected.
        The host name is implicitly derived from a setup variable.

        Args:
            cmd: command that should be executed
            exit_status: return code of the command

        Returns:
            None

        """

        Utils.validate_string(u'cmd', cmd)
        Utils.validate_argument(u'exit_status', exit_status)

    @keyword('Command ${cmd:".+"} exits with status ${exit_status:([0-9]{1,3\})|("[0-9]{1,3\}")} and ${stream:stdout|stderr} contains ${stream_content:".+"}')
    def command_with_stream(self, cmd=None, exit_status=None, stream='stdout', stream_content=None):
        """
        Validates that an environment variable is set on a specific host.
        The host name is implicitly derived from a setup variable.

        Args:
            stream: output stream (stdout or stderr)
            exit_status: return code of the command
            cmd: the command that should be executed
            stream_content: string that is expected in the specified output stream
            operator: the validation operation to perform

        Returns:
            None

        """

        Utils.validate_string(u'cmd', cmd)
        Utils.validate_argument(u'exit_status', exit_status)
        Utils.validate_argument(u'stream', stream)
        Utils.validate_string(u'stream_content', stream_content)

    @keyword('Process ${process:\S+\s|".+"\s}${operator:is|is not} running')
    def process(self, process=None, operator='is'):
        """
        Validates that a process is running on the target machine.
        The host name is implicitly derived from a setup variable.

        Args:
            operator: is or is not
            process: command that should be executed

        Returns:
            None

        """

        Utils.validate_string(u'process', process)
        Utils.validate_string(u'operator', operator)

    @keyword('Service ${service:\S+\s|".+"\s}${operator:is|is not} running')
    def service(self, service=None, operator='is'):
        """
        Validates that a service is running on the target machine.
        The host name is implicitly derived from a setup variable.

        Args:
            operator: is or is not
            service: command that should be executed

        Returns:
            None

        """

        Utils.validate_string(u'service', service)
        Utils.validate_string(u'operator', operator)

    @keyword('Package ${package:\S+\s} ${version:\S+\s} ${operator:is|is not} installed')
    def package(self, package=None, version='', operator='is'):
        """
        Validates that a package is or is not installed on the target machine.
        The host name is implicitly derived from a setup variable.

        Args:
            version: expected version number
            operator: is or is not
            package: command that should be executed

        Returns:
            None

        """

        Utils.validate_string(u'package', package)
        Utils.validate_string(u'operator', operator)

    @keyword('Kernel parameter ${param:\S+} ${operator:is|is not} set to ${value:\d+}')
    def package(self, parameter=None, operator='is', value=None):
        """
        Validates that a package is or is not installed on the target machine.
        The host name is implicitly derived from a setup variable.

        Args:
            parameter: expected version number
            operator: is or is not
            value: command that should be executed

        Returns:
            None

        """

        Utils.validate_string(u'parameter', parameter)
        Utils.validate_string(u'operator', operator)
        Utils.validate_string(u'value', value)

    @keyword('${instance:(^\S+)|(^[I,i]nstance)} ${operator:is|is not} running on ${host:\S+}')
    def placement_node(self, instance=None, operator='is', host=None):
        """
        Validates that an instance runs on specific host.

        Args:
            operator: is or is not
            instance: expected version number
            host: machine where the instance should run

        Returns:
            None

        """
        Utils.validate_string(u'instance', instance)
        Utils.validate_string(u'operator', operator)
        Utils.validate_string(u'host', host)

    @keyword('Host of ${instance:(\S+)|([i,I]nstance)} ${operator:has|has not} label ${label:"\S+"}')
    def placement_label(self, instance=None, operator='has', label=None):
        """
        Validates that an instance runs on a host with a specific label.

        Args:
            operator: has or has not
            label: label name
            instance: expected version number

        Returns:
            None
        """

        self.placement_labels(instance, operator, label)


    @keyword('Host of ${instance:(\S+)|([i,I]nstance)} ${operator:has|has not} labels ${labels:\[("\S+",?\s*)+\]}')
    def placement_labels(self, instance=None, operator='has', labels=None):
        """
        Validates that an instance runs on a host with specific labels.

        Args:
            operator: has or has not
            labels: list of labels
            instance: expected version number

        Returns:
            None
        """
        if labels is None:
            labels = []
        if not isinstance(labels, list):
            labels = list(labels)

        Utils.validate_string(u'instance', instance)
        Utils.validate_string(u'labels', labels)

    @keyword('Host of ${instance:(\S+)|([i,I]nstance)} ${operator:has|has not} role ${role:"\S+"}')
    def placement_role(self, instance=None, operator='has', role=None):
        """
        Validates that an instance runs on a host with a specific role.

        Args:
            operator: has or has not
            role: role name
            instance: expected version number

        Returns:
            None
        """

        self.placement_roles(instance, operator, role)

    def _get_context(self):
        s = TestSuite()
        d = TestData()
        logger.info('')
