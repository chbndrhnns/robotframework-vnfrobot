# -*- coding: utf-8 -*-
from robot.libraries.BuiltIn import BuiltIn, RobotNotRunningError

from robot.api.deco import keyword

from ValidationTargets.CommandTarget import Command
from ValidationTargets.FileTarget import File
from ValidationTargets.PlacementTarget import Placement
from exc import SetupError, NotFoundError, DataFormatError, ValidationError
from ValidationTargets.AddressTarget import Address
from ValidationTargets.PortTarget import Port
from ValidationTargets.VariableTarget import Variable
from settings import Settings
from tools import orchestrator, matchers
from ValidationTargets.context import set_context
from robotlibcore import DynamicCore
from tools.data_structures import SUT
from version import VERSION
from tools.matchers import string_matchers, all_matchers


class VnfValidator(DynamicCore):
    """The VnfValidator module contains low-level keywords for the VNF Robot."""

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
            'USE_DEPLOYMENT': None
        }
        self.test_volume = None
        self.sidecar = None
        self.services = []
        self.containers = []

        try:
            self.deployment_options['USE_DEPLOYMENT'] = (BuiltIn().get_variable_value("${USE_DEPLOYMENT}") or '').strip('\'')
            if self.deployment_options['USE_DEPLOYMENT'] or BuiltIn().get_variable_value("${SKIP_UNDEPLOY}"):
                self.deployment_options['SKIP_UNDEPLOY'] = True
        except RobotNotRunningError:
            pass

    # noinspection PyUnusedLocal
    def _start_suite(self, name, attrs):
        self.suite_source = attrs.get('source', None)
        self.descriptor_file = BuiltIn().get_variable_value("${DESCRIPTOR}") or 'docker-compose.yml'

        try:
            orchestrator.get_or_create_deployment(self)
        except SetupError as exc:
            BuiltIn().fatal_error(exc)

    # noinspection PyUnusedLocal
    def _end_suite(self, name, attrs):
        orchestrator.remove_deployment(self)

    def update_sut(self, **kwargs):
        # create a new namedtuple and use the old values if no new value is available
        # noinspection PyProtectedMember
        temp_sut = self.sut._replace(
            target_type=kwargs.get('target_type', self.sut.target_type),
            target=kwargs.get('target', self.sut.target),
            service_id=kwargs.get('service_id', self.sut.service_id),
        )

        try:
            self.sut = self._check_sut_availability(temp_sut)

            BuiltIn().log('\nUpdating context: target_type={}, service_id={}, target={}'.format(
                self.sut.target_type if self.sut.target_type else 'Not set',
                self.sut.service_id if self.sut.service_id else 'Not set',
                self.sut.target if self.sut.target else 'Not set'),
                    level='INFO', console=Settings.to_console)
        except NotFoundError as exc:
            raise NotFoundError('update_sut: Fatal error: {} "{}" not found in deployment "{}".'.format(temp_sut.target_type, temp_sut.target, self.deployment_name))

    def _check_sut_availability(self, temp_sut):
        try:
            if temp_sut.target_type == 'network':
                self.docker_controller.get_network(temp_sut.service_id)
            elif temp_sut.target_type == 'service':
                self.docker_controller.get_service(temp_sut.service_id)
            elif temp_sut.target_type == 'container':
                self.docker_controller.get_containers(filters={
                                                          'name': temp_sut.service_id
                                                      },
                                                      all=True)
            else:
                raise NotFoundError('_check_sut_availability: target_type {} is invalid'.format(temp_sut.target_type))
            return temp_sut
        except NotFoundError as exc:
            raise exc

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

    @keyword('Command ${{raw_entity:{}}}: ${{raw_prop:{}}} ${{matcher:{}}} ${{raw_val:{}}}'.format(
        matchers.quoted_or_unquoted_string,
        '|'.join(Command.properties.keys()),
        '|'.join(all_matchers.keys()),
        matchers.quoted_or_unquoted_string))
    def command_kw(self, raw_entity, raw_prop, matcher, raw_val):
        try:
            validation_target = Command(self)
            validation_target.set_as_dict({
                'context': self.sut,
                'entity': raw_entity,
                'property': raw_prop,
                'matcher': matcher,
                'value': raw_val})
            validation_target.run_test()
        except (DataFormatError, ValidationError) as exc:
            BuiltIn().fail(exc)

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

    @keyword('File ${{raw_entity:{}}}: ${{matcher:{}}} ${{raw_val:{}}}'.format(
        matchers.quoted_or_unquoted_string,
        '|'.join(string_matchers.keys()),
        matchers.quoted_or_unquoted_string))
    def file_kw_content(self, raw_entity, matcher, raw_val):
        try:
            validation_target = File(self)
            validation_target.set_as_dict({
                'context': self.sut,
                'entity': raw_entity,
                'property': 'content',
                'matcher': matcher,
                'value': raw_val})
            validation_target.run_test()
        except (DataFormatError, ValidationError) as exc:
            BuiltIn().fail(exc)

    @keyword('File ${{raw_entity:{}}}: ${{raw_prop:{}}} ${{matcher:{}}} ${{raw_val:{}}}'.format(
        matchers.quoted_or_unquoted_string,
        '|'.join(File.properties.keys()),
        '|'.join(all_matchers.keys()),
        matchers.quoted_or_unquoted_string))
    def file_kw(self, raw_entity, raw_prop, matcher, raw_val):
        try:
            validation_target = File(self)
            validation_target.set_as_dict({
                'context': self.sut,
                'entity': raw_entity,
                'property': raw_prop,
                'matcher': matcher,
                'value': raw_val})
            validation_target.run_test()
        except (DataFormatError, ValidationError) as exc:
            BuiltIn().fail(exc)

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

    @keyword('Placement: ${{raw_prop:{}}} ${{matcher:{}}} ${{raw_val:\S+}}'.format(
        '|'.join(Placement.properties.keys()),
        '|'.join(string_matchers.keys())))
    def placement_kw(self, raw_prop, matcher, raw_val):
        try:
            validation_target = Placement(self)
            validation_target.set_as_dict({
                'context': self.sut,
                'entity': 'placement',
                'property': raw_prop,
                'matcher': matcher,
                'value': raw_val})
            validation_target.run_test()
        except (DataFormatError, ValidationError) as exc:
            BuiltIn().fail(exc)

    @keyword('Remove deployment')
    def remove_deployment_kw(self):
        orchestrator.remove_deployment(self)
