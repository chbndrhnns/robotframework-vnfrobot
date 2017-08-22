# -*- coding: utf-8 -*-


from unittest import TestCase

from DockerOrchestrator import DockerOrchestrator
from SuiteSetup import SuiteSetup, SetupError


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

    def test__setup__pass(self):
        # prepare
        setup_class = SuiteSetup()

        # do
        setup_class.setup(project_path=self.project_path)

        # check
        self.assertIsInstance(setup_class.orchestrator, DockerOrchestrator)
