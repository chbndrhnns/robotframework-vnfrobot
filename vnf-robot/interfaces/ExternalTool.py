from abc import ABCMeta, abstractmethod, abstractproperty

import os

from exc import ArgumentMissingException, InvalidPathException
from settings import Settings


class ExternalTool(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.settings = Settings()
        self.available = False

    @abstractmethod
    def get_instance(self):
        """
        Get an instance of the orchestrator.

        """
        raise NotImplementedError('{__name__} must be implemented.'.format(**self.__dict__))

    @staticmethod
    def check_availability(path):
        """
        Checks whether a path to a tool is valid and the tool is executable.

        Args:
            path: str

        Returns: Boolean

        """
        if path is None:
            raise ArgumentMissingException('Path is needed to check availability.')

        real_path = os.path.realpath(path)

        # try to resolve path and check if tool is executable
        if os.path.isfile(real_path) and os.access(real_path, os.X_OK):
                return True
        else:
            raise InvalidPathException('Cannot resolve path {} or not executable'.format(real_path))





