# -*- coding: utf-8 -*-
from unittest import TestCase

import docker
import requests
from docker.errors import DockerException
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

    @patch('DockerOrchestrator.docker.client.APIClient.get')
    def test__get_instance__no_explicit_host__pass(self, get):
        # prepare
        get.return_value = requests.Response()
        get.return_value.status = 200

        # do
        try:
            self.orchestrator.get_instance()
        except DockerException as exc:
            self.fail('get_instance() should not fail with "{}"'.format(exc.__repr__()))

    @patch('DockerOrchestrator.docker.client.APIClient.get')
    def test__get_instance__explicit_host__pass(self, get):
        # prepare
        get.return_value = requests.Response()
        get.return_value.status = 200

        hosts = [
            'unix:///var/run/docker.sock',
            'tcp://128.104.222.48:2376'
        ]

        # do
        try:
            for host in hosts:
                self.orchestrator.settings.docker['DOCKER_HOST'] = host
                self.orchestrator.get_instance()
        except DockerException as exc:
            self.fail('get_instance() should not fail with "{}"'.format(exc.__repr__()))

    @patch('DockerOrchestrator.docker.api.daemon.DaemonApiMixin.ping')
    def test__get_instance__host_unreachable__exception(self, ping):
        # prepare
        ping.side_effect = docker.errors.APIError(message='')
        self.orchestrator.settings.docker['DOCKER_HOST'] = 'unix:///var/run/docker.sock'

        # do
        with self.assertRaises(docker.errors.APIError):
            self.orchestrator.get_instance()

        # check
        self.assertEqual(ping.call_count, 1)
