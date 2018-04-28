from abc import ABCMeta, abstractmethod

from exc import SetupError
from tools.data_structures import SUT


class ValidationTarget():
    __metaclass__ = ABCMeta

    def __init__(self, instance=None):
        self.instance = instance
        self.test_result = None

        # sut
        self.sut = None

        self.entity = None
        self.property = None
        self.matcher = None
        self.value = None

    def get_as_dict(self):
        return {
            'context': getattr(self, 'context', None),
            'entity': getattr(self, 'entity', None),
            'property': getattr(self, 'property', None),
            'matcher': getattr(self, 'matcher', None),
            'value': getattr(self, 'value', None)
        }

    def get(self, prop):
        return getattr(self, prop, None)

    def set(self, prop, value):
        try:
            if isinstance(value, basestring):
                value = value.strip('"\'\n')
            setattr(self, prop, unicode(value))
        except AttributeError:
            raise

    def set_as_dict(self, data=None):
        if data is None:
            data = {}

        for key, val in data.iteritems():
            try:
                self.set(key, val)
            except AttributeError:
                raise

    @abstractmethod
    def validate(self):
        pass

    @abstractmethod
    def transform(self):
        pass

    @abstractmethod
    def run_test(self):
        pass

    def _find_robot_instance(self):
        if not self.instance:
            raise SetupError('No robot instance found.')
        if not isinstance(self.instance.sut, SUT):
            raise SetupError('No SUT declared.')

    def _check_test_data(self):
        missing = [key for key, value in self.get_as_dict().iteritems() if not value]
        if missing:
            raise ValueError('No value for {}'.format(missing))
