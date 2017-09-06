# -*- coding: utf-8 -*-
from unittest import TestCase

from mock import patch

from DockerOrchestrator import DockerOrchestrator
from tests import SetupError


class DockerOrchestratorTest(TestCase):
    def setUp(self):
        self.orchestrator = DockerOrchestrator()
        self.project_path = 'fixtures/docker-compose'

    def test__parse_descriptor__valid_descriptor__pass(self):
        # do
        self.orchestrator.parse_descriptor('fixtures/')

        # check
        self.assertIsNotNone(self.orchestrator.project)

    def test__validate_descriptor__valid_descriptor__pass(self):
        # prepare
        self.orchestrator.parse_descriptor(self.project_path)
        expected_services = ['web', 'redis']
        expected_networks = ['default']
        expected_volumes = []

        # do
        self.orchestrator.validate_descriptor()

        # check
        self.assertEqual(self.orchestrator.services, expected_services)
        self.assertEqual(self.orchestrator.volumes, expected_volumes)
        self.assertEqual(self.orchestrator.networks, expected_networks)

    @patch('DockerOrchestrator.TopLevelCommand.up', return_value=0)
    def test__create_infrastructure__pass(self, command):
        # Prepare
        self.orchestrator.parse_descriptor('fixtures/')

        # do
        try:
            self.orchestrator.create_infrastructure()
        except Exception as exc:
            self.fail('Exception "{}" raised.'.format(exc.message))

        # check
        self.assertEqual(command.call_count, 1)

    @patch('DockerOrchestrator.TopLevelCommand.up', return_value=1)
    def test__create_infrastructure__exception(self, command):
        # Prepare
        self.orchestrator.parse_descriptor('fixtures/')

        # do
        with self.assertRaises(SetupError):
            self.orchestrator.create_infrastructure()

        # check
        self.assertEqual(command.call_count, 1)

    @patch('DockerOrchestrator.TopLevelCommand.up', return_value=0)
    @patch('DockerOrchestrator.TopLevelCommand.down', return_value=1)
    def test__stop_infrastructure__pass(self, down, up):
        # prepare
        self.orchestrator.parse_descriptor('fixtures/')
        self.orchestrator.create_infrastructure()
        down.return_value = None

        # do
        self.orchestrator.destroy_infrastructure()

        # check
        self.assertEqual(up.call_count, 1)
        self.assertEqual(down.call_count, 1)

    # def test__get_instance__unix_socket__pass(self):
    #     # prepare
    #
    #     self.orchestrator.get_instance()
    #
    #
    #     # do
    #
    #     # check

    # @patch('DockerOrchestrator.TopLevelCommand.down', return_value=1)
    # def test__get_instance__docker_mac__pass(self, down):
    #     # prepare
    #     self.orchestrator.parse_descriptor('fixtures/')
    #     self.orchestrator.create_infrastructure()
    #     down.return_value = None
    #
    #     # do
    #     self.orchestrator.destroy_infrastructure()
    #
    #     # check
    #     self.assertEqual(up.call_count, 1)
    #     self.assertEqual(down.call_count, 1)
