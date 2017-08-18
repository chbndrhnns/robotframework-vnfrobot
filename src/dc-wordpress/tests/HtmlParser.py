import HTMLParser
import inspect
import pdb

from bs4 import BeautifulSoup
from robot.api.deco import keyword
from robot.api import logger
from version import VERSION
from robotlibcore import DynamicCore


class DataError(RuntimeError):
    ROBOT_EXIT_ON_FAILURE = True


class HtmlParser(DynamicCore):
    """HtmlParser parses a HTML string and offers methods to find and extract elements to verify them."""

    ROBOT_LIBRARY_SCOPE = 'TEST CASE'
    __version__ = VERSION

    def __init__(self):
        DynamicCore.__init__(self, [])

        logger.info("Importing {}".format(self.__class__))

        self.raw_text = None
        self.soup = None

    def run_keyword(self, name, args, kwargs):
        """
        Mandatory method for using robot dynamic libraries

        Returns:
            None
        """
        logger.info("Running keyword '%s' with arguments %s." % (name, args))
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
            raise DataError('HTM data missing.')

        self.soup = BeautifulSoup(html, 'lxml')

    @keyword('Verify title equals ${title}')
    def get_title(self, title=None):
        """
        Checks that the title of a HTML document matches a given string.

        Args:
            title: expected title

        Returns:
            Boolean: verification failed/passed

        """
        if title is None:
            raise DataError('Title missing.')

        if self.soup.title.string == title:
            return True
        return False
