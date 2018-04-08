from unittest import TestCase

from mock import patch

from integrations.Goss import Goss


class TestGoss(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @patch('integrations.Goss.ExternalTool.check_availability')
    def test___init__pass(self, mock_avail):
        # prepare
        mock_avail.return_value = True

        settings = {
            'path': '/usr/bin/goss'
        }

        # run
        Goss(settings=settings)

        # check
        self.assertEqual(mock_avail.call_count, 1)

    # def test__