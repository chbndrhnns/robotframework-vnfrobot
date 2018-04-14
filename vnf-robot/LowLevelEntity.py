from abc import ABCMeta, abstractmethod

from exc import SetupError
from modules.context import SUT


class LowLevelEntity():
    __metaclass__ = ABCMeta

    def __init__(self, instance=None):
        self.instance = instance
        self.properties = {}
        self.test_result = None

        # context
        self.context = None
        self.valid_contexts = []

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

    @abstractmethod
    def validate(self):
        pass

    @abstractmethod
    def transform(self):
        pass

    @abstractmethod
    def run_test(self):
        pass

    @abstractmethod
    def evaluate_results(self):
        pass

    def _check_instance(self):
        if not self.instance:
            raise SetupError('No robot instance found.')
        if not isinstance(self.instance.sut, SUT):
            raise SetupError('No SUT declared.')

    def _check_data(self):
        missing = [key for key, value in self.get_as_dict().iteritems() if not value]
        if missing:
            raise ValueError('No value for {}'.format(missing))