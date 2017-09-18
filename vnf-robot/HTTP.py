# -*- coding: utf-8 -*-


from RequestsLibrary import RequestsLibrary
from requests import ConnectTimeout
from urllib3.exceptions import ConnectTimeoutError, ResponseError

from Utils import Utils
from exc import *
from robot.api import logger
from robot.api.deco import keyword
from robotlibcore import DynamicCore
from version import VERSION


class HTTP(DynamicCore):
    """HTTP wraps requests to HTTP servers. Internally the `robot-requestslibrary` is used."""

    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'
    __version__ = VERSION

    def __init__(self):
        DynamicCore.__init__(self, [])

        logger.info("Importing {}".format(self.__class__))

        self.requests_lib = RequestsLibrary()
        self.soup = None

    def run_keyword(self, name, args, kwargs):
        """
        Mandatory method for using robot dynamic libraries

        Returns:
            None
        """
        logger.info("Running keyword '%s' with arguments %s." % (name, args))
        return self.keywords[name](*args, **kwargs)

    @keyword('GET ${url}')
    def get_simple(self, url=None):
        """
        Issues an HTTP GET request to the specified url.

        Args:
            url: URL that is retrieved

        Returns:
            None

        """
        if url is None:
            raise DataError('URL data missing.')

        try:
            url_params = Utils.get_url_attributes(url)
        except DataError as exc:
            raise
        alias = "{}-{}".format(url_params['host'], Utils.generate_uuid())

        try:
            self.requests_lib.create_session(alias=alias,
                                             url=url_params['host'],
                                             max_retries=self.settings.http_max_retries,
                                             disable_warnings=True)
            response = self.requests_lib.get_request(alias=alias,
                                                     uri=url_params['path'],
                                                     timeout=self.settings.http_get_timeout)
        except ConnectTimeout as exc:
            raise TimeoutError(u'Cannot reach {}: {}'.format(url, exc))

        return response
