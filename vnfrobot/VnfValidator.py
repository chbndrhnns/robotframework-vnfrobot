# -*- coding: utf-8 -*-
import os

from rflint.parser import parser
from robot.libraries.BuiltIn import BuiltIn, RobotNotRunningError

from robot.api.deco import keyword

from ValidationTargets.CommandTarget import Command
from ValidationTargets.FileTarget import File
from ValidationTargets.PlacementTarget import Placement
from exc import SetupError, NotFoundError, DataFormatError, ValidationError
from ValidationTargets.AddressTarget import Address
from ValidationTargets.PortTarget import Port
from ValidationTargets.VariableTarget import Variable
from settings import Settings, set_breakpoint
from tools import matchers
from ValidationTargets.context import set_context
from robotlibcore import DynamicCore
from tools.data_structures import SUT
from tools.orchestrator import DockerOrchestrator
from version import VERSION
from tools.matchers import string_matchers, all_matchers


class VnfValidator(DynamicCore):
    """
    The VnfValidator is the base library that contains low-level keywords for the VNF Robot.
    The class implements the DynamicCore interface provided by the Robot Framework.

    For every test suite, one instance of the class is created.
    """

    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'
    ROBOT_LISTENER_API_VERSION = 2
    __version__ = VERSION

    def __init__(self):
        DynamicCore.__init__(self, [])
        self.ROBOT_LIBRARY_LISTENER = self

        # inputs
        self.descriptor_file = None
        self.suite_source = None
        self.parsed_descriptor = None

        # Suite config
        self.deployment_name = None
        self.orchestrator = None

        # Test case config
        self.sut = SUT(None, None, None)
        self.deployment_options = {
            'SKIP_UNDEPLOY': False,
            'USE_DEPLOYMENT': None
        }
        self.test_volume = None
        self.sidecar = None
        self.services = []
        self.containers = []

        # keep state of test
        self.context = None
        self.test_cases = []
        self.current_keywords = []
        self.fatal_error = False
        self.validation_attempted = False

        try:
            self.deployment_options['USE_DEPLOYMENT'] = \
                (Settings.use_deployment or
                 BuiltIn().get_variable_value("${USE_DEPLOYMENT}") or '').strip('\'')
            if (self.deployment_options['USE_DEPLOYMENT'] or
                    BuiltIn().get_variable_value("${SKIP_UNDEPLOY}") or
                    Settings.skip_undeploy):
                self.deployment_options['SKIP_UNDEPLOY'] = True
        except RobotNotRunningError:
            pass

    # noinspection PyUnusedLocal
    def _start_suite(self, name, attrs):
        """
        Listener method by the Robot Framework that is called when on suite setup.

        Args:
            name: name of the suite
            attrs: attributes of the suite

        Returns:
            None

        """
        self.suite_source = attrs.get('source', None)
        self.descriptor_file = BuiltIn().get_variable_value("${DESCRIPTOR}") or 'docker-compose.yml'

        # parse robot file
        self.parsed_descriptor = parser.RobotFactory(self.suite_source)
        self.test_cases = [t for t in self.parsed_descriptor.testcases]
        assert self.test_cases, "A robot file should contain test cases."

        # comment out check of test steps
        # if not self._check_test_steps():
        #     return
        try:
            BuiltIn().log('\nOptions: {}'.format(self.deployment_options),
                          level='INFO',
                          console=True)
            self.orchestrator = DockerOrchestrator(self)
            self.orchestrator.get_or_create_deployment()
        except SetupError as exc:
            BuiltIn().log('_start_suite: {}'.format(exc), level='ERROR')
            self.fatal_error = True

    def _check_test_steps(self):
        """
        Helper method to check if for every test case in the suite, there is at least one command for
        setting the context and one validation statement

        Returns:
            True: if the conditions are met
            False: if the conditions are not met

        """
        for test_case in self.test_cases:
            context_steps_count = len([step for step in test_case.steps if len(step) > 1 and 'context' in step[1]])
            if (len(test_case.steps) - context_steps_count) < 1:
                BuiltIn().log('_start_suite: Error with Test case: \n"{}"\n'
                              'Every test case requires at least ONE context statement and ONE validation statement'
                              .format(test_case.name), level='ERROR')
                self.fatal_error = True
                return False
        return True

    # noinspection PyUnusedLocal
    def _end_suite(self, name, attrs):
        """
            Listener method by the Robot Framework that is called when on suite setup.

            Args:
                name: name of the suite
                attrs: attributes of the suite

            Returns:
                None
        """
        if self.orchestrator:
            self.orchestrator.remove_deployment()

    def update_sut(self, **kwargs):
        """
        Update the sut object with the values provided in **kwargs.

        Before the update takes place, we check if the updated SUT is available.

        Args:
            **kwargs: target_type, target, service_id

        Returns:
            None

        """
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
            raise NotFoundError(
                'update_sut: Fatal error: {} "{}" not found in deployment "{}".'.format(temp_sut.target_type,
                                                                                        temp_sut.target,
                                                                                        self.deployment_name))

    def _check_sut_availability(self, temp_sut):
        """
        Helper method to determine if an SUT is available. Makes use of the Orchestrator instance.

        Args:
            temp_sut: namedtuple

        Returns:
            temp_sut: namedtuple

        """
        try:
            if temp_sut.target_type == 'network':
                self.orchestrator.controller.get_network(temp_sut.service_id)
            elif temp_sut.target_type == 'service':
                self.orchestrator.controller.get_service(temp_sut.service_id)
            elif temp_sut.target_type == 'container':
                self.orchestrator.controller.get_containers(filters={
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
        Mandatory method in dynamic libraries of the Robot Framework. Gets called by the framework if a keyword was
        identified as belonging to that library.

        Returns:
            None
        """
        self.context = BuiltIn().get_library_instance(all=True)

        # logger.info(u"\nRunning keyword '%s' with arguments %s." % (name, args), also_console=True)
        return self.keywords[name](*args, **kwargs)

    @keyword('Set ${context_type:\S+} context to ${context:\S+}')
    def set_context_kw(self, context_type=None, context=None):
        """
        Keyword 'Set context'

        Args:
            context_type: str
            context: str

        Returns:
            None

        """
        try:
            set_context(self, context_type, context)
        except (NotFoundError, SetupError) as exc:
            BuiltIn().fatal_error(exc)

    @keyword('Command ${{raw_entity:{}}}: ${{raw_prop:{}}} ${{matcher:{}}} ${{raw_val:{}}}'.format(
        matchers.quoted_or_unquoted_string,
        '|'.join(Command.properties.keys()),
        '|'.join(all_matchers.keys()),
        matchers.quoted_or_unquoted_string))
    def command_kw(self, raw_entity, raw_prop, matcher, raw_val):
        """
        'Command' keyword.

        Args:
            raw_entity: str
            raw_prop: str
            matcher: str
            raw_val: str

        Returns:
            None

        """
        try:
            validation_target = Command(self)
            validation_target.set_as_dict({
                'context': self.sut,
                'entity': raw_entity,
                'property': raw_prop,
                'matcher': matcher,
                'value': raw_val})
            validation_target.run_test()
        except ValidationError as exc:
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
        """
        'File' keyword (no property)

        Args:
            raw_entity: str
            matcher: str
            raw_val: str

        Returns:
            None

        """
        try:
            validation_target = File(self)
            validation_target.set_as_dict({
                'context': self.sut,
                'entity': raw_entity,
                'property': 'content',
                'matcher': matcher,
                'value': raw_val})
            validation_target.run_test()
        except ValidationError as exc:
            BuiltIn().fail(exc)

    @keyword('File ${{raw_entity:{}}}: ${{raw_prop:{}}} ${{matcher:{}}} ${{raw_val:{}}}'.format(
        matchers.quoted_or_unquoted_string,
        '|'.join(File.properties.keys()),
        '|'.join(all_matchers.keys()),
        matchers.quoted_or_unquoted_string))
    def file_kw(self, raw_entity, raw_prop, matcher, raw_val):
        """
        'File' keyword (with property)

        Args:
            raw_entity: str
            raw_prop: str
            matcher: str
            raw_val: str

        Returns:
            None

        """
        try:
            validation_target = File(self)
            validation_target.set_as_dict({
                'context': self.sut,
                'entity': raw_entity,
                'property': raw_prop,
                'matcher': matcher,
                'value': raw_val})
            validation_target.run_test()
        except ValidationError as exc:
            BuiltIn().fail(exc)

    @keyword('Symbolic Link')
    def symlink_kw(self):
        pass

    @keyword('Address ${{raw_entity:\S+}}: ${{matcher:{}}} ${{raw_val:\S+}}'.format('|'.join(string_matchers.keys())))
    def address_kw(self, raw_entity, matcher, raw_val):
        """
        'Address' keyword

        Args:
            raw_entity: str
            matcher: str
            raw_val: str

        Returns:
            None

        """
        try:
            entity = Address(self)
            entity.set_as_dict({
                'context': self.sut,
                'entity': raw_entity,
                'matcher': matcher,
                'value': raw_val})
            entity.run_test()
        except ValidationError as exc:
            BuiltIn().fail(exc)

    @keyword('DNS')
    def dns_kw(self):
        pass

    @keyword('Interface')
    def interface_kw(self):
        pass

    @keyword('Variable ${{raw_entity:{}}}: ${{matcher:{}}} ${{raw_val:{}}}'.format(
        matchers.quoted_or_unquoted_string,
        '|'.join(string_matchers.keys()),
        matchers.quoted_or_unquoted_string))
    def env_variable_kw(self, raw_entity, matcher, raw_val):
        """
        'Variable' keyword

        Args:
            raw_entity: str
            matcher: str
            raw_val: str

        Returns:
            None

        """
        try:
            validation_target = Variable(self)
            validation_target.set_as_dict({
                'context': self.sut,
                'entity': raw_entity,
                'matcher': matcher,
                'value': raw_val})
            validation_target.run_test()
        except ValidationError as exc:
            BuiltIn().fail(exc)

    @keyword('Port ${{raw_entity:\S+}}: ${{raw_prop:{}}} ${{matcher:{}}} ${{raw_val:\S+}}'.format(
        '|'.join(Port.properties.keys()),
        '|'.join(string_matchers.keys())))
    def port_kw(self, raw_entity, raw_prop, matcher, raw_val):
        """
        'Port' keyword

        Args:
            raw_entity: str
            raw_prop: str
            matcher: str
            raw_val: str

        Returns:
            None

        """
        try:
            validation_target = Port(self)
            validation_target.set_as_dict({
                'context': self.sut,
                'entity': raw_entity,
                'property': raw_prop,
                'matcher': matcher,
                'value': raw_val})
            validation_target.run_test()
        except ValidationError as exc:
            BuiltIn().fail(exc)

    @keyword('Placement: ${{raw_prop:{}}} ${{matcher:{}}} ${{raw_val:\S+}}'.format(
        '|'.join(Placement.properties.keys()),
        '|'.join(string_matchers.keys())))
    def placement_kw(self, raw_prop, matcher, raw_val):
        """
        'Placement' keyword

        Args:
            raw_prop: str
            matcher: str
            raw_val: str

        Returns:
            None

        """
        try:
            validation_target = Placement(self)
            validation_target.set_as_dict({
                'context': self.sut,
                'entity': 'placement',
                'property': raw_prop,
                'matcher': matcher,
                'value': raw_val})
            validation_target.run_test()
        except ValidationError as exc:
            BuiltIn().fail(exc)

    @keyword('Remove deployment')
    def remove_deployment_kw(self):
        """
        'Remove deployment' keyword

        Returns:
            None

        """
        self.orchestrator.remove_deployment(self)
