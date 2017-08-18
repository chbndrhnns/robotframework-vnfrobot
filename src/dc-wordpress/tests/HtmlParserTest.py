# -*- coding: utf-8 -*-


from HtmlParser import HtmlParser
from unittest import TestCase
from bs4 import BeautifulSoup

from exc import *




class HtmlParserTest(TestCase):
    valid_html = ['<html><head><title>Test title</title></head><body>Test body</body></html>',
                  '<html><head><title>WordPress &rsaquo; Installation</title><meta http-equiv="Content-Type" '
                  'content="text/html; charset=utf-8" /></head><body>Test body</body></html>']
    empty_html = ''

    def setUp(self):
        self.parser = HtmlParser()

    def tearDown(self):
        pass

    def test__parse_html__valid_html__pass(self):
        for code in self.valid_html:
            self.parser.parse_html(html=code)

    def test__parse_html__empty_html__pass(self):
        self.parser.parse_html(html=self.empty_html)

    def test__parse_html__None_html__exception(self):
        with self.assertRaises(DataError) as exc:
            self.parser.parse_html(html=None)
            self.assertEqual(exc.value.message, 'HTML data missing.')

    def test__verify_title__match__pass(self):
        for code in self.valid_html:
            # prep
            self.parser.parse_html(html=code)
            expected = BeautifulSoup(code, 'lxml').title.string

            # do
            self.parser.verify_title(title=expected)

    def test__verify_title__mismatch__exception(self):
        for code in self.valid_html:
            # prep
            self.parser.parse_html(html=code)
            expected = "Title Mismatch"

            # do
            with self.assertRaises(DataError) as exc:
                result = self.parser.verify_title(title=expected)

                self.assertIn(expected, exc.value.message)

    def test__verify_title__None_title_exception(self):
        for code in self.valid_html:
            # prep
            self.parser.parse_html(html=code)
            expected = BeautifulSoup(code, 'lxml').title.string

            # do & check
            with self.assertRaises(DataError) as exc:
                self.assertTrue(self.parser.verify_title(title=None))
                self.assertEqual(exc.value.message, 'Title missing.')
