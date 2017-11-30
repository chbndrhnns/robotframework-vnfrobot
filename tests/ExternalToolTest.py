from unittest import TestCase

from mock import patch

import settings
from exc import ArgumentMissingException, InvalidPathException
from interfaces.ExternalTool import ExternalTool


class TestExternalTool(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test__check_availability__no_parameter__exception(self):
        # run
        with self.assertRaisesRegexp(ArgumentMissingException, 'Path is needed'):
            ExternalTool.check_availability(path=None)

    def test__check_availability__invalid_path__exception(self):
        # run
        with self.assertRaisesRegexp(InvalidPathException, 'Cannot resolve'):
            ExternalTool.check_availability('invalidPathxxx')

    @patch('os.path.isfile')
    @patch('os.access')
    def test__check_availability__not_executable__exception(self, mock_access, mock_isfile):
        mock_access.return_value = 0
        mock_isfile.return_value = True

        # run
        with self.assertRaisesRegexp(InvalidPathException, 'Cannot resolve'):
            ExternalTool.check_availability('some_path')

        # check
        self.assertEqual(mock_access.call_count, 1)
        self.assertEqual(mock_isfile.call_count, 1)

    @patch('os.path.isfile')
    @patch('os.access')
    def test__check_availability__not_executable__exception(self, mock_access, mock_isfile):
        mock_access.return_value = 1
        mock_isfile.return_value = True

        # run
        ExternalTool.check_availability('some_path')

        # check
        self.assertEqual(mock_access.call_count, 1)
        self.assertEqual(mock_isfile.call_count, 1)

