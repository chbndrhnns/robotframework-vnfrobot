from abc import ABCMeta, abstractmethod, abstractproperty


class Orchestrator(object):
    __metaclass__ = ABCMeta

    teardown_levels = ['stop', 'clean', 'destroy']

    def __init__(self):
        pass

    @abstractmethod
    def get_instance(self):
        """
        Get an instance of the orchestrator.

        """
        raise NotImplementedError('{__name__} must be implemented.'.format(**self.__dict__))

    @abstractmethod
    def parse_descriptor(self, project_path):
        """
        Parses a descriptor using the mechanism of the Orchestrator.

        """
        raise NotImplementedError('{__name__} must be implemented.'.format(**self.__dict__))

    @abstractmethod
    def validate_descriptor(self):
        """
        Validates a descriptor using the mechanism of the Orchestrator.

        """
        raise NotImplementedError('{__name__} must be implemented.'.format(**self.__dict__))

    @abstractmethod
    def create_infrastructure(self):
        """
        Creates infrastructure according to descriptor using the mechanism of the Orchestrator.

        """
        raise NotImplementedError('{__name__} must be implemented.'.format(**self.__dict__))

    @abstractmethod
    def destroy_infrastructure(self):
        """
        Destroys infrastructure using the mechanism of the Orchestrator.

        """
        raise NotImplementedError('{__name__} must be implemented.'.format(**self.__dict__))
