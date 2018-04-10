# -*- coding: utf-8 -*-
import namesgenerator

from robot.libraries.BuiltIn import BuiltIn

from robot.api import logger
from robot.api.deco import keyword

from exc import SetupError
from modules import variable, port
from tools import orchestrator
from modules.context import set_context, SUT
from robotlibcore import DynamicCore
from version import VERSION
from testutils import string_matchers, validate_deployment


class LowLevel(DynamicCore):
    """The LowLevel module contains low-level keywords for the VNF Robot."""

    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'
    ROBOT_LISTENER_API_VERSION = 2
    __version__ = VERSION

    def __init__(self):
        DynamicCore.__init__(self, [])
        self.descriptor_file = None
        self.deployment_name = None
        self.context_type = None
        self.context = None
        self.sut = SUT(None, None)
        self.ROBOT_LIBRARY_LISTENER = self
        self.suite_source = None
        self.containers_created = []
        self.services_created = []
        self.docker_controller = None
        self.deployment_result = None
        self.deployment_options = {
            'SKIP_DEPLOY': False,
            'SKIP_UNDEPLOY': False,
        }

        logger.info(u"Importing {}".format(self.__class__))

        if BuiltIn().get_variable_value("${SKIP_DEPLOY}"):
            self.deployment_options['SKIP_DEPLOY'] = True

        if BuiltIn().get_variable_value("${SKIP_UNDEPLOY}"):
            self.deployment_options['SKIP_UNDEPLOY'] = True

        if BuiltIn().get_variable_value("${DEPLOYMENT_NAME}"):
            self.deployment_name = BuiltIn().get_variable_value("${DEPLOYMENT_NAME}")
        else:
            self.deployment_name = namesgenerator.get_random_name()

    def _start_suite(self, name, attrs):
        self.suite_source = attrs.get('source', None)
        self.descriptor_file = BuiltIn().get_variable_value("${DESCRIPTOR}")
        self.deploy_kw(self.descriptor_file)

    def _end_suite(self, name, attrs):
        if self.deployment_options['SKIP_DEPLOY']:
            logger.console('Skipping undeployment')
            return

        if self.docker_controller and self.descriptor_file:
            logger.debug('Removing deployment "{}"'.format(self.descriptor_file))
            self.remove_deployment_kw()
        else:
            logger.console('Skipping: remove deployment')

    def run_keyword(self, name, args, kwargs):
        """
        Mandatory method for using robot dynamic libraries

        Returns:
            None
        """
        self.context = BuiltIn().get_library_instance(all=True)
        validate_deployment(self)

        # logger.info(u"\nRunning keyword '%s' with arguments %s." % (name, args), also_console=True)
        return self.keywords[name](*args, **kwargs)

    @keyword('Set ${context_type:\S+} context to ${context:\S+}')
    def set_context_kw(self, context_type=None, context=None):
        self.sut = set_context(context_type, context)

    @keyword('Command')
    def command_kw(self):
        pass

    @keyword('Process')
    def process_kw(self):
        pass

    @keyword('Service')
    def service_kw(self):
        pass

    @keyword('Kernel Parameter')
    def kernel_parameter_kw(self):
        pass

    @keyword('Container')
    def container_kw(self):
        pass

    @keyword('User')
    def user_kw(self):
        pass

    @keyword('Group')
    def group_kw(self):
        pass

    @keyword('File')
    def file_kw(self):
        pass

    @keyword('Symbolic Link')
    def symlink_kw(self):
        pass

    @keyword('Address')
    def address_kw(self):
        pass

    @keyword('DNS')
    def dns_kw(self):
        pass

    @keyword('Interface')
    def interface_kw(self):
        pass

    @keyword('Variable ${{raw_entity:\S+}}: ${{matcher:{}}} ${{raw_val:\S+}}'.format('|'.join(string_matchers.keys())))
    def env_variable_kw(self, raw_entity, matcher, raw_val):
        variable.validate(self, raw_entity, matcher, raw_val)

    @keyword('Port ${{raw_entity:\S+}}: ${{raw_prop:\S+}} ${{matcher:{}}} ${{raw_val:\S+}}'.format(
        '|'.join(string_matchers.keys())))
    def port_kw(self, raw_entity, raw_prop, matcher, raw_val):
        port.validate(self, raw_entity, raw_prop, matcher, raw_val)

    @keyword('Deploy ${descriptor:\S+}')
    def deploy_kw(self, descriptor):
        try:
            self.deployment_result = orchestrator.deploy(self, descriptor)
        except SetupError as exc:
            BuiltIn().fail(exc)

    @keyword('Remove deployment')
    def remove_deployment_kw(self):
        orchestrator.undeploy(self)
