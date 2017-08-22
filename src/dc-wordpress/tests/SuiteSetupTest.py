# -*- coding: utf-8 -*-


from unittest import TestCase

import os
from robot.api import logger
from mock import patch

from DockerOrchestrator import DockerOrchestrator
from SuiteSetup import SuiteSetup
from exc import SetupError, ConnectionError


class SuiteSetupTest(TestCase):
    def setUp(self):
        self.project_base_path = os.path.join(os.getcwd(), 'fixtures/')

    def test__setup__no_project_path__exception(self):
        # prepare
        setup_class = SuiteSetup()

        # do
        with self.assertRaises(SetupError) as exc:
            setup_class.setup()

        # check
        self.assertIn('project_path', str(exc.exception))

    @patch('DockerOrchestrator.TopLevelCommand.up')
    def test__setup__no_connection__exception(self, up_command):
        # prepare
        setup_class = SuiteSetup()
        up_command.side_effect = ConnectionError('Could not connect to url=', ['', 'http'])

        # do & check
        with self.assertRaisesRegexp(ConnectionError, 'url='):
            setup_class.setup(project_path=os.path.join(self.project_base_path, 'docker-compose'))

    def test__setup__invalid_dockercompose_file__exception(self):
        # prepare
        setup_class = SuiteSetup()

        # do & check
        with self.assertRaisesRegexp(SetupError, 'docker-compose'):
            setup_class.setup(project_path=os.path.join(self.project_base_path, 'docker-compose-invalid'))

    def test__setup__path_invalid__exception(self):
        # prepare
        setup_class = SuiteSetup()

        # do & check
        with self.assertRaisesRegexp(SetupError, 'No docker-compose file found in'):
            setup_class.setup(project_path=os.path.join(self.project_base_path, 'docker-compose-missing-compose-file'))

    def test__setup__no_dockercompose_file__exception(self):
        # prepare
        setup_class = SuiteSetup()

        # do & check
        with self.assertRaisesRegexp(SetupError, u'docker-compose'):
            setup_class.setup(project_path=os.path.join(self.project_base_path, 'docker-compose-missing-compose-file'))

    @patch('SuiteSetup.os.path.getsize')
    def test__setup__empty_docker_compose_file__exception(self, getsize):
        # prepare
        from docker.errors import APIError
        getsize.side_effect = [0]
        setup_class = SuiteSetup()

        # do & check
        with self.assertRaisesRegexp(SetupError, u'docker-compose file must not be empty'):
            setup_class.setup(project_path=os.path.join(self.project_base_path, 'docker-compose'))

        self.assertEqual(getsize.call_count, 1)

    @patch('SuiteSetup.os.path.getsize')
    def test__setup__empty_dockerfile__exception(self, getsize):
        # prepare
        getsize.side_effect = [127, 0]
        setup_class = SuiteSetup()

        # do & check
        with self.assertRaisesRegexp(SetupError, u'Dockerfile must not be empty'):
            setup_class.setup(project_path=os.path.join(self.project_base_path, 'docker-compose'))

        self.assertEqual(getsize.call_count, 2)

    def test__setup__no_dockerfile__exception(self):
        # prepare
        setup_class = SuiteSetup()

        # do & check
        with self.assertRaisesRegexp(SetupError, 'Dockerfile'):
            setup_class.setup(project_path=os.path.join(self.project_base_path, 'docker-compose-missing-Dockerfile'))

    @patch('DockerOrchestrator.TopLevelCommand.up')
    def test__setup__pass(self, up_command):
        # prepare
        setup_class = SuiteSetup()
        up_command.return_value = None

        # do
        setup_class.setup(project_path=os.path.join(self.project_base_path, 'docker-compose'))

        # check
        self.assertIsInstance(setup_class.orchestrator, DockerOrchestrator)
        self.assertEqual(up_command.call_count, 1)
