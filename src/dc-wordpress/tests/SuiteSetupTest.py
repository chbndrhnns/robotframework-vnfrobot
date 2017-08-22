# -*- coding: utf-8 -*-


from unittest import TestCase
from robot.api import logger
from mock import patch

from DockerOrchestrator import DockerOrchestrator
from SuiteSetup import SuiteSetup
from exc import SetupError, ConnectionError


class SuiteSetupTest(TestCase):
    def setUp(self):
        self.project_path = 'fixtures/'

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

        # do
        with self.assertRaisesRegexp(ConnectionError, 'url='):
            setup_class.setup(project_path=self.project_path)


    def test__setup__pass(self):
        # prepare
        setup_class = SuiteSetup()

        # do
        setup_class.setup(project_path=self.project_path)

        # check
        self.assertIsInstance(setup_class.orchestrator, DockerOrchestrator)
