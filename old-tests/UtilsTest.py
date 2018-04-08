# -*- coding: utf-8 -*-


from unittest import TestCase
from uuid import UUID

from Utils import Utils


class UtilsTest(TestCase):
    def setUp(self):
        self.utils = Utils()

    def tearDown(self):
        pass

    def test__generate_uuid__pass(self):
        # do
        uuid = self.utils.generate_uuid()

        # check
        self.assertEqual(str(uuid), str(UUID(str(uuid))))

    def test__get_url_attribute__valid_uris__pass(self):
        # prep
        uris = {
            'http://www.google.de': {
                'host': 'http://www.google.de',
                'path': '/'},
            'https://www.news.co.uk': {
                'host': 'https://www.news.co.uk',
                'path': '/'},
            'https://www.telekom.de:8888/bla?index=5000': {
                'host': 'https://www.telekom.de:8888',
                'path': '/bla'},
            'http://thatis.a.verylong.domain.name.eu/bla': {
                'host': 'http://thatis.a.verylong.domain.name.eu',
                'path': '/bla'},
            'https://www.telekom.de/product1/details/verydetailed': {
                'host': 'https://www.telekom.de',
                'path': '/product1/details/verydetailed'},
        }

        # do
        for uri, expected in uris.iteritems():
            ret_val = self.utils.get_url_attributes(uri)
            self.assertTrue(ret_val == expected)
