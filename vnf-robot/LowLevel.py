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

from DockerController import DockerController
from robotlibcore import DynamicCore
from version import VERSION

SUT = collections.namedtuple('sut', 'target_type, target')


class LowLevel(DynamicCore):
    """The LowLevel module contains low-level keywords for the VNF Robot."""

    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'
    ROBOT_LISTENER_API_VERSION = 2
    __version__ = VERSION

    def __init__(self):
        DynamicCore.__init__(self, [])
        self.descriptor_file = None
        self.deployment_name = namesgenerator.get_random_name()
        self.context_type = None
        self.context = None
        self.sut = SUT(None, None)
        self.ROBOT_LIBRARY_LISTENER = self
        self.suite_source = None
        self.containers_created = []
        self.services_created = []
        self.docker_controller = None

        logger.info(u"Importing {}".format(self.__class__))

    def _start_suite(self, name, attrs):
        self.suite_source = attrs.get('source', None)

        self.descriptor_file = BuiltIn().get_variable_value("${DESCRIPTOR}")
        if not BuiltIn().get_variable_value("${SKIP_DEPLOY}"):
            logger.console('Deploying {}'.format(self.descriptor_file))
            self.deploy(self.descriptor_file)
        else:
            logger.console('Skipping deployment')

    def _end_suite(self, name, attrs):
        if BuiltIn().get_variable_value("${SKIP_UNDEPLOY}"):
            logger.console('Skipping undeployment')
            return

        if self.docker_controller:
            logger.console('Removing deployment "{}"'.format(self.descriptor_file))
            self.remove_deployment()
        else:
            logger.console('Skipping: remove deployment')

    def run_keyword(self, name, args, kwargs):
        """
        Mandatory method for using robot dynamic libraries

        Returns:
            None
        """
        self.context = BuiltIn().get_library_instance(all=True)

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

    @keyword('Environment Variable')
    def env_variable(self):
        allowed_context = ('node',)

        if self.sut.target_type not in allowed_context:
            raise exc.SetupError('Context type "{}" not allowed.'.format(self.sut.target_type))

        return dict([('OS_USERNAME', 'admin'), ('OS_AUTH_URL', 'http://localhost:5000/api')])

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

    @keyword('Port ${raw_entity:\S+}: ${property:\S+} is ${val:\S+}')
    def port(self, raw_entity, raw_prop, raw_val):
        allowed_context = ['service', 'network']
        properties = {
            'state': ['open', 'closed']
        }

        self.validate_context(allowed_context)
        self.validate_port(raw_entity)

        self.validate_property(properties, raw_prop)
        self.validate_value(properties, raw_prop, raw_val)

    @keyword('Deploy ${descriptor:\S+}')
    def deploy(self, descriptor):
        if self.suite_source is None:
            raise exc.SetupError('Cannot determine directory of robot file.')

        self.descriptor_file = descriptor

        self.docker_controller = DockerController(base_dir=os.path.dirname(self.suite_source))
        self.docker_controller.dispatch(['stack', 'deploy', '-c', self.descriptor_file, self.deployment_name])

    @keyword('Remove deployment')
    def remove_deployment(self):
        self.docker_controller.dispatch(['stack', 'rm', self.deployment_name])

    @staticmethod
    def validate_value(properties, raw_prop, raw_val):
        val = raw_val in properties[raw_prop]
        if not val:
            raise exc.ValidationError(
                'Value "{}" not allowed for {}. Must be any of {}'.format(raw_val, raw_prop, properties.keys()))

    @staticmethod
    def validate_property(properties, raw_prop):
        # Check that the given property and its expected value are valid
        prop = raw_prop in properties
        if not prop:
            raise exc.ValidationError(
                'Property "{}" not allowed. Must be any of {}'.format(raw_prop, properties.keys()))

    @staticmethod
    def validate_port(raw_entity):
        # Check that raw_entity is valid
        # 0 < port <= 65535
        # \d+
        entity = re.search('(\d+)[/]?(tcp|udp)?', raw_entity, re.IGNORECASE)
        if not entity:
            raise exc.ValidationError(
                'Port "{}" not valid.'.format(raw_entity))
        port = int(entity.group(1)) if entity else None
        protocol = lower(entity.group(2)) if entity.group(2) else None
        if not (0 < port <= 65535):
            raise exc.ValidationError(
                'Port "{}" not valid. Must be between 1 and 65535'.format(port))
        elif protocol:
            if protocol not in ['tcp', 'udp']:
                raise exc.ValidationError(
                    'Protocol "{}" not valid. Only udp and tcp are supported'.format(protocol))

    def validate_context(self, allowed_context):
        # Check that a context is given for the test
        if self.sut.target_type not in allowed_context:
            raise exc.SetupError(
                'Context type "{}" not allowed. Must be any of {}'.format(self.sut.target_type, allowed_context))
