# -*- coding: utf-8 -*-
import cgi

from bs4 import BeautifulSoup

import exc
from robot.api import logger
from robot.api.deco import keyword
from robotlibcore import DynamicCore
from version import VERSION


class HtmlParser(DynamicCore):
    """HtmlParser parses a HTML string and offers methods to find and extract elements to verify them."""

    ROBOT_LIBRARY_SCOPE = 'TEST CASE'
    __version__ = VERSION

    def __init__(self):
        DynamicCore.__init__(self, [])

        logger.info(u"Importing {}".format(self.__class__))

        self.raw_text = None
        self.soup = None

    def run_keyword(self, name, args, kwargs):
        """
        Mandatory method for using robot dynamic libraries

        Returns:
            None
        """
        logger.info(u"Running keyword '%s' with arguments %s." % (name, args))
        return self.keywords[name](*args, **kwargs)

    @keyword('Parse')
    def parse_html(self, html=None):
        """
        Parse a string into a Beautifulsoup object for finding elements.

        Args:
            html: valid string containing HTML data

        Returns:
            None

        """
        if html is None:
            raise exc.DataError(u'HTML data missing.')

        self.soup = BeautifulSoup(html, 'lxml')

    @keyword(u'Assert that title equals ${title}')
    def verify_title(self, title=None):
        """
        Checks that the title of a HTML document matches a given string.

        Args:
            title: expected title

        Returns:
            Boolean: verification failed/passed

        """
        if title is None:
            raise exc.DataError(u'Title missing.')

        expected_title = unicode(self.soup.title.string)

        processed_title = title.strip('"')
        processed_title = unicode(cgi.escape(processed_title))

        if expected_title != processed_title:
            raise exc.AssertError(
                u"Titles do not match: \n\t'{}' is not '{}'".format(processed_title, expected_title))
