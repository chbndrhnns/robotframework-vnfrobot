# -*- coding: utf-8 -*-


from unittest import TestCase
import responses

from HTTP import HTTP, DataError


class HTTPTest(TestCase):
    def setUp(self):
        self.http = HTTP()

    def tearDown(self):
        pass

    def test__get_simple__no_url__exception(self):
        # do & check
        with self.assertRaises(DataError) as exc:
            self.http.get_simple(url=None)
            self.assertEqual(exc.value.message, 'URL data missing')

    @responses.activate
    def test__get_simple__valid_url__pass(self):
        # prepare
        url = 'https://www.doesnotexist.de/'
        body = 'Bla'
        responses.add(responses.GET, url=url, body=body)
        expected = {'text': body, 'status_code': 200}

        # do
        response = self.http.get_simple(url)

        # check
        assert len(responses.calls) == 1
        assert responses.calls[0].request.url == url
        self.assertEqual(expected['text'], response.text)
        self.assertEqual(expected['status_code'], response.status_code)

    def test__get_simple__invalid_url__exception(self):
        # prepare
        url = 'feorhgdughagh;h;aeuhrg'
        body = 'Bla'
        expected = {'text': body, 'status_code': 200}

        # do
        with self.assertRaises(DataError) as exc:
            self.http.get_simple(url)

            self.assertIn('Invalid URL', exc.value.message)
