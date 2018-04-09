# -*- coding: utf-8 -*-
import collections
import re
from string import lower
import namesgenerator

import os
from robot.libraries.BuiltIn import BuiltIn

import exc
from robot.api import logger
from robot.api.deco import keyword

from DockerController import DockerController, ProcessResult
from robotlibcore import DynamicCore
from version import VERSION
from testutils import string_matchers, number_matchers, get_truth, validate_context, validate_port, validate_property, \
    validate_value, validate_against_regex

SUT = collections.namedtuple('sut', 'target_type, target')


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
        self.deployment_result = ProcessResult('', '')
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
        logger.console('Deploying {}'.format(self.descriptor_file))
        self.deployment_result = self.deploy(self.descriptor_file)

    def _end_suite(self, name, attrs):
        if self.deployment_options['SKIP_DEPLOY']:
            logger.console('Skipping undeployment')
            return

        if self.docker_controller:
            logger.console('Removing deployment "{}"'.format(self.descriptor_file))
            self.remove_deployment()
        else:
            logger.console('Skipping: remove deployment')

    def validate_deployment(self):
        if self.deployment_result.stderr:
            BuiltIn().fatal_error("Could not deploy the system under test: {}".format(self.deployment_result.stderr))

    def run_keyword(self, name, args, kwargs):
        """
        Mandatory method for using robot dynamic libraries

        Returns:
            None
        """
        self.context = BuiltIn().get_library_instance(all=True)

        logger.console('\nValidating deployment results...')
        self.validate_deployment()

        logger.info(u"\nRunning keyword '%s' with arguments %s." % (name, args), also_console=True)

        # if self.deployment is None and u'Deploy ${descriptor:\\S+}' not in name:
        #     raise exc.SetupError('The "Deploy" keyword is necessary before running any other keyword.')

        return self.keywords[name](*args, **kwargs)

    @keyword('Set ${context_type:\S+} context to ${context:\S+}')
    def set_context(self, context_type=None, context=None):
        context_types = ['application', 'service', 'node', 'network']

        if context_type not in context_types:
            raise exc.SetupError('Invalid context given. Must be {}'.format(context_types))
        if context is None:
            raise exc.SetupError('No context given.')

        self.sut = SUT(context_type, context)

    @keyword('Command')
    def command(self):
        allowed_context = ('node',)

        if self.sut.target_type not in allowed_context:
            raise exc.SetupError('Context type "{}" not allowed.'.format(self.sut.target_type))

        return dict([('OS_USERNAME', 'admin'), ('OS_AUTH_URL', 'http://localhost:5000/api')])

    @keyword('Process')
    def process(self):
        allowed_context = ('node',)

        if self.sut.target_type not in allowed_context:
            raise exc.SetupError('Context type "{}" not allowed.'.format(self.sut.target_type))

        return dict([('OS_USERNAME', 'admin'), ('OS_AUTH_URL', 'http://localhost:5000/api')])

    @keyword('Service')
    def service(self):
        allowed_context = ('node',)

        if self.sut.target_type not in allowed_context:
            raise exc.SetupError('Context type "{}" not allowed.'.format(self.sut.target_type))

        return dict([('OS_USERNAME', 'admin'), ('OS_AUTH_URL', 'http://localhost:5000/api')])

    @keyword('Kernel Parameter')
    def kernel_parameter(self):
        allowed_context = ('node',)

        if self.sut.target_type not in allowed_context:
            raise exc.SetupError('Context type "{}" not allowed.'.format(self.sut.target_type))

        return dict([('OS_USERNAME', 'admin'), ('OS_AUTH_URL', 'http://localhost:5000/api')])

    @keyword('Container')
    def container(self):
        allowed_context = ('node',)

        if self.sut.target_type not in allowed_context:
            raise exc.SetupError('Context type "{}" not allowed.'.format(self.sut.target_type))

        return dict([('OS_USERNAME', 'admin'), ('OS_AUTH_URL', 'http://localhost:5000/api')])

    @keyword('User')
    def user(self):
        allowed_context = ('node',)

        if self.sut.target_type not in allowed_context:
            raise exc.SetupError('Context type "{}" not allowed.'.format(self.sut.target_type))

        return dict([('OS_USERNAME', 'admin'), ('OS_AUTH_URL', 'http://localhost:5000/api')])

    @keyword('Group')
    def group(self):
        allowed_context = ('node',)

        if self.sut.target_type not in allowed_context:
            raise exc.SetupError('Context type "{}" not allowed.'.format(self.sut.target_type))

        return dict([('OS_USERNAME', 'admin'), ('OS_AUTH_URL', 'http://localhost:5000/api')])

    @keyword('File')
    def file(self):
        allowed_context = ('node',)

        if self.sut.target_type not in allowed_context:
            raise exc.SetupError('Context type "{}" not allowed.'.format(self.sut.target_type))

        return dict([('OS_USERNAME', 'admin'), ('OS_AUTH_URL', 'http://localhost:5000/api')])

    @keyword('Symbolic Link')
    def symlink(self):
        allowed_context = ('node',)

        if self.sut.target_type not in allowed_context:
            raise exc.SetupError('Context type "{}" not allowed.'.format(self.sut.target_type))

        return dict([('OS_USERNAME', 'admin'), ('OS_AUTH_URL', 'http://localhost:5000/api')])

    @keyword('Address')
    def address(self):
        allowed_context = ('node',)

        if self.sut.target_type not in allowed_context:
            raise exc.SetupError('Context type "{}" not allowed.'.format(self.sut.target_type))

        return dict([('OS_USERNAME', 'admin'), ('OS_AUTH_URL', 'http://localhost:5000/api')])

    @keyword('DNS')
    def dns(self):
        allowed_context = ('node',)

        if self.sut.target_type not in allowed_context:
            raise exc.SetupError('Context type "{}" not allowed.'.format(self.sut.target_type))

        return dict([('OS_USERNAME', 'admin'), ('OS_AUTH_URL', 'http://localhost:5000/api')])

    @keyword('Interface')
    def interface(self):
        allowed_context = ('node',)

        if self.sut.target_type not in allowed_context:
            raise exc.SetupError('Context type "{}" not allowed.'.format(self.sut.target_type))

        return dict([('OS_USERNAME', 'admin'), ('OS_AUTH_URL', 'http://localhost:5000/api')])

    @keyword('Variable ${{raw_entity:\S+}}: ${{matcher:{}}} ${{raw_val:\S+}}'.format('|'.join(string_matchers.keys())))
    def env_variable(self, raw_entity, matcher, raw_val):
        allowed_context = ['service']
        raw_entity_matcher = '[A-Z][A-Z0-9_]'
        raw_value_matcher = '[^\s]'
        service_id = '{}_{}'.format(self.deployment_name, self.sut.target)

        value = raw_val.strip('"\'')

        # Validations
        validate_context(allowed_context, self.sut.target_type)
        validate_against_regex('variable', raw_entity, raw_entity_matcher)
        validate_against_regex('value', value, raw_value_matcher)

        # Get data
        env = self.docker_controller.get_env(service_id)
        found = [e.split('=')[1] for e in env if raw_entity in e.split('=')[0]][0]

        if not found:
            raise exc.ValidationError('No variable {} found.'.format(raw_entity))

        if not get_truth(found, string_matchers[matcher], value):
            raise exc.ValidationError('Variable {}: {} {}'.format(raw_entity, matcher, value))

    @keyword('Port ${raw_entity:\S+}: ${property:\S+} is ${val:\S+}')
    def port(self, raw_entity, raw_prop, raw_val):
        allowed_context = ['service', 'network']
        properties = {
            'state': ['open', 'closed']
        }

        # Validations
        validate_context(allowed_context, self.sut.target_type)
        validate_port(raw_entity)
        validate_property(properties, raw_prop)
        validate_value(properties, raw_prop, raw_val)

        # Test

    @keyword('Deploy ${descriptor:\S+}')
    def deploy(self, descriptor):
        if self.suite_source is None:
            raise exc.SetupError('Cannot determine directory of robot file.')

        self.descriptor_file = descriptor

        self.docker_controller = DockerController(base_dir=os.path.dirname(self.suite_source))
        if self.deployment_options['SKIP_DEPLOY']:
            logger.console('Skipping deployment')
        else:
            return self.docker_controller.dispatch(
                ['stack', 'deploy', '-c', self.descriptor_file, self.deployment_name])

    @keyword('Remove deployment')
    def remove_deployment(self):
        self.docker_controller.dispatch(['stack', 'rm', self.deployment_name])
        self.docker_controller = None
