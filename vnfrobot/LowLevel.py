# -*- coding: utf-8 -*-
import collections

from robot.libraries.BuiltIn import BuiltIn, RobotNotRunningError

from robot.api import logger
from robot.api.deco import keyword

from exc import SetupError, NotFoundError, DataFormatError, ValidationError
from modules.address import Address
from modules.port import Port
from modules.variable import Variable
from tools import orchestrator
from modules.context import set_context
from robotlibcore import DynamicCore
from tools.data_structures import SUT
from version import VERSION
from tools.testutils import string_matchers


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
        self.sut = SUT(None, None, None)
        self.ROBOT_LIBRARY_LISTENER = self
        self.suite_source = None
        self.docker_controller = None
        self.deployment_options = {
            'SKIP_UNDEPLOY': False,
        }
        self.test_volume = None
        self.services = []

        logger.info(u"Importing {}".format(self.__class__))

        try:
            if BuiltIn().get_variable_value("${SKIP_UNDEPLOY}"):
                self.deployment_options['SKIP_UNDEPLOY'] = True

            self.deployment_name = BuiltIn().get_variable_value("${USE_DEPLOYMENT}")
        except RobotNotRunningError:
            pass

    def _start_suite(self, name, attrs):
        self.suite_source = attrs.get('source', None)
        self.descriptor_file = BuiltIn().get_variable_value("${DESCRIPTOR}")

        self.deploy_kw(self.descriptor_file)

    def _end_suite(self, name, attrs):
        if self.deployment_options['SKIP_UNDEPLOY']:
            logger.console('Skipping undeployment')
            return

        if self.docker_controller and self.descriptor_file:
            logger.debug('Removing deployment "{}"'.format(self.descriptor_file))
            self.remove_deployment_kw()
        else:
            logger.console('Skipping: remove deployment')

    def update_sut(self, **kwargs):
        self.sut = self.sut._replace(**kwargs)
        BuiltIn().log('\nUpdating context: type={}, service={}, target={}'.format(
            self.sut.target_type,
            self.sut.service_id,
            self.sut.target),
            level='INFO', console=True)

    def run_keyword(self, name, args, kwargs):
        """
        Mandatory method for using robot dynamic libraries

        Returns:
            None
        """
        self.context = BuiltIn().get_library_instance(all=True)

        # logger.info(u"\nRunning keyword '%s' with arguments %s." % (name, args), also_console=True)
        return self.keywords[name](*args, **kwargs)

    @keyword('Set ${context_type:\S+} context to ${context:\S+}')
    def set_context_kw(self, context_type=None, context=None):
        try:
            set_context(self, context_type, context)
        except NotFoundError as exc:
            BuiltIn().fatal_error(exc)

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

    @keyword('Address ${{raw_entity:\S+}}: ${{matcher:{}}} ${{raw_val:\S+}}'.format('|'.join(string_matchers.keys())))
    def address_kw(self, raw_entity, matcher, raw_val):
        try:
            entity = Address(self)
            entity.set_as_dict({
                'context': self.sut,
                'entity': raw_entity,
                'matcher': matcher,
                'value': raw_val})
            entity.run_test()
        except (DataFormatError, ValidationError) as exc:
            BuiltIn().fail(exc)

    @keyword('DNS')
    def dns_kw(self):
        pass

    @keyword('Interface')
    def interface_kw(self):
        pass

    @keyword('Variable ${{raw_entity:\S+}}: ${{matcher:{}}} ${{raw_val:\S+}}'.format('|'.join(string_matchers.keys())))
    def env_variable_kw(self, raw_entity, matcher, raw_val):
        try:
            validation_target = Variable(self)
            validation_target.set_as_dict({
                'context': self.sut,
                'entity': raw_entity,
                'matcher': matcher,
                'value': raw_val})
            validation_target.run_test()
        except (DataFormatError, ValidationError) as exc:
            BuiltIn().fail(exc)

    @keyword('Port ${{raw_entity:\S+}}: ${{raw_prop:{}}} ${{matcher:{}}} ${{raw_val:\S+}}'.format(
        '|'.join(Port.properties.keys()),
        '|'.join(string_matchers.keys())))
    def port_kw(self, raw_entity, raw_prop, matcher, raw_val):
        try:
            validation_target = Port(self)
            validation_target.set_as_dict({
                'context': self.sut,
                'entity': raw_entity,
                'property': raw_prop,
                'matcher': matcher,
                'value': raw_val})
            validation_target.run_test()
        except (DataFormatError, ValidationError) as exc:
            BuiltIn().fail(exc)

    @keyword('Deploy ${descriptor:\S+}')
    def deploy_kw(self, descriptor):
        if self.descriptor_file is None:
            BuiltIn().log('No descriptor file specified. Assuming fake deployment...', level='INFO', console=True)
            return
        try:
            orchestrator.deploy(self, descriptor)
        except SetupError as exc:
            BuiltIn().fatal_error(exc)

    @keyword('Remove deployment')
    def remove_deployment_kw(self):
        orchestrator.undeploy(self)
