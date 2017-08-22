# -*- coding: utf-8 -*-
import shutil
from backports import tempfile
from unittest import TestCase

import os
from robot.api import logger
from mock import patch

from DockerOrchestrator import DockerOrchestrator
from SuiteTools import SuiteTools
from exc import SetupError, ConnectionError


class SuiteToolsTest(TestCase):
    def setUp(self):
        self.project_base_path = os.path.join(os.getcwd(), 'fixtures/')
        self.setup_class = SuiteTools()

    def test__setup__no_project_path__exception(self):
        # do
        with self.assertRaises(SetupError) as exc:
            self.setup_class.setup()

        # check
        self.assertIn('project_path', str(exc.exception))

    @patch('DockerOrchestrator.TopLevelCommand.up')
    def test__setup__no_connection__exception(self, up_command):
        # prepare
        up_command.side_effect = ConnectionError('Could not connect to url=', ['', 'http'])

        # do & check
        with self.assertRaisesRegexp(ConnectionError, 'url='):
            self.setup_class.setup(project_path=os.path.join(self.project_base_path, 'docker-compose'))

    def test__setup__invalid_dockercompose_file__exception(self):
        # do & check
        with self.assertRaisesRegexp(SetupError, 'docker-compose'):
            self.setup_class.setup(project_path=os.path.join(self.project_base_path, 'docker-compose-invalid'))

    def test__setup__path_invalid__exception(self):
        # do & check
        with self.assertRaisesRegexp(SetupError, 'No docker-compose file found in'):
            self.setup_class.setup(
                project_path=os.path.join(self.project_base_path, 'docker-compose-missing-compose-file'))

    def test__setup__no_dockercompose_file__exception(self):
        # do & check
        with self.assertRaisesRegexp(SetupError, u'docker-compose'):
            self.setup_class.setup(
                project_path=os.path.join(self.project_base_path, 'docker-compose-missing-compose-file'))

    @patch('SuiteTools.os.path.getsize')
    def test__setup__empty_docker_compose_file__exception(self, getsize):
        # prepare
        getsize.side_effect = [0]

        # do & check
        with self.assertRaisesRegexp(SetupError, u'docker-compose file must not be empty'):
            self.setup_class.setup(project_path=os.path.join(self.project_base_path, 'docker-compose'))

        self.assertEqual(getsize.call_count, 1)

    @patch('SuiteTools.os.path.getsize')
    def test__setup__empty_dockerfile__exception(self, getsize):
        # prepare
        getsize.side_effect = [127, 0]

        # do & check
        with self.assertRaisesRegexp(SetupError, u'Dockerfile must not be empty'):
            self.setup_class.setup(project_path=os.path.join(self.project_base_path, 'docker-compose'))

        self.assertEqual(getsize.call_count, 2)

    def test__setup__no_dockerfile__exception(self):
        # do & check
        with self.assertRaisesRegexp(SetupError, 'Dockerfile'):
            self.setup_class.setup(
                project_path=os.path.join(self.project_base_path, 'docker-compose-missing-Dockerfile'))

    @patch('DockerOrchestrator.TopLevelCommand.up')
    def test__setup__pass(self, up_command):
        # prepare
        up_command.return_value = None

        # do
        self.setup_class.setup(project_path=os.path.join(self.project_base_path, 'docker-compose'))

        # check
        self.assertIsInstance(self.setup_class.orchestrator, DockerOrchestrator)
        self.assertEqual(up_command.call_count, 1)

    @patch('DockerOrchestrator.TopLevelCommand.up')
    def test__setup__outside_project_path__pass(self, up_command):
        with tempfile.TemporaryDirectory() as destination:
            # prepare
            src = os.path.join(self.project_base_path, 'docker-compose')
            shutil.copyfile(os.path.join(src, 'Dockerfile'), os.path.join(destination, 'Dockerfile'))
            shutil.copyfile(os.path.join(src, 'docker-compose.yml'), os.path.join(destination, 'docker-compose.yml'))
            up_command.return_value = None

            # do
            self.setup_class.setup(project_path=destination)

            # check
            self.assertIsInstance(self.setup_class.orchestrator, DockerOrchestrator)
            self.assertEqual(up_command.call_count, 1)
