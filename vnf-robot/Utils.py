# -*- coding: utf-8 -*-


import uuid
from string import lower
from urlparse import urlparse

from requests.exceptions import InvalidSchema

from exc import *


class Utils:
    def __init__(self):
        pass

    @staticmethod
    def get_url_attributes(url):
        """
        Takes URL and splits it after the hostname or port.

        Args:
            url: URL to process

        Returns:
            dict:

        """
        params = {}
        try:
            if 'http' not in lower(url):
                raise InvalidSchema

            o = urlparse(url)

            params['host'] = "{}://{}".format(o.scheme, o.netloc)
            params['path'] = o.path
            if o.path is '':
                params['path'] = '/'
        except InvalidSchema as exc:
            raise DataError('Invalid URL: {}'.format(url))

        return params

    @staticmethod
    def generate_uuid():
        return str(uuid.uuid4())
