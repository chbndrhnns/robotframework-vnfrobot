from HtmlParser import HtmlParser, DataError
from unittest import TestCase, SkipTest, BaseTestSuite
from bs4 import BeautifulSoup

from tests import EmptyArgumentException


class HtmlParserTest(TestCase):
    valid_html = '<html><head><title>Test title</title><body>Test body</body></html>'
    empty_html = ''

    def setUp(self):
        self.parser = HtmlParser()

    def tearDown(self):
        pass

    def test__parse_html__valid_html__pass(self):
        self.parser.parse_html(html=self.valid_html)

    def test__parse_html__empty_html__pass(self):
        self.parser.parse_html(html=self.empty_html)

    def test__parse_html__none_html__exception(self):
        with self.assertRaises(DataError) as exc:
            self.parser.parse_html(html=None)
            self.assertEqual(exc.value.message, 'HTML data missing.')

    def test__get_title__pass(self):
        # prep
        self.parser.parse_html(html=self.valid_html)
        expected = BeautifulSoup(self.valid_html, 'lxml').title.string

        # do
        result = self.parser.get_title(title=expected)

        # check
        self.assertTrue(result)

    def test__get_title__None_title_exception(self):
        # prep
        self.parser.parse_html(html=self.valid_html)
        expected = BeautifulSoup(self.valid_html, 'lxml').title.string

        # do & check
        with self.assertRaises(DataError) as exc :
            self.assertTrue(self.parser.get_title(title=None))
            self.assertEqual(exc.value.message, 'Title missing.')
