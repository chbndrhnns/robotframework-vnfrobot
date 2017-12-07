# -*- coding: utf-8 -*-
import json
import uuid
from string import lower
from urlparse import urlparse

from requests.exceptions import InvalidSchema

import exc
from exc import *


class Utils:
    def __init__(self):
        pass

    @staticmethod
    def validate_argument(argument_name, value):
        value = value.strip()
        if value is None:
            raise exc.DataError(u'Argument \'{}\' is not valid: must not be None.'.format(argument_name))
        if len(value) is 0:
            raise exc.DataError(u'Argument \'{}\' is not valid: must not be empty.'.format(argument_name))
        if u' ' in value and argument_name != u'operator':
            raise exc.DataError(u'Argument \'{}\' is not valid: must not contain spaces.'.format(argument_name))

    @staticmethod
    def validate_json(argument_name, value):
        value = value.strip()
        try:
            json.loads(value)
        except (ValueError, TypeError) as exc:
            raise exc.DataError(u'Argument \'{}\' is not valid: must not be JSON.'.format(argument_name))

    @staticmethod
    def validate_string(argument_name, value):
        if value is None:
            raise exc.DataError(u'Argument \'{}\' is not valid: must not be None.'.format(argument_name))
        if len(value) is 0:
            raise exc.DataError(u'Argument \'{}\' is not valid: must not be empty.'.format(argument_name))

    @staticmethod
    def validate_list(argument_name, value):
        if value is None:
            raise exc.DataError(u'Argument \'{}\' is not valid: must not be None.'.format(argument_name))
        if not isinstance(value, list):
            raise exc.DataError(u'Argument \'{}\' is not valid: must be a list [ "..." ].'.format(argument_name))

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

