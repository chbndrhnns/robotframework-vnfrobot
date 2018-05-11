from abc import ABCMeta, abstractmethod, abstractproperty


class ValueTransformer:
    __metaclass__ = ABCMeta

    def __init__(self, data):
        self.data = data
        assert self.data, 'Cannot instantiate ValueTransformer class without providing data.'

    @abstractproperty
    def transformed(self):
        raise NotImplementedError('Needs implementing.')


class GossFileModeTransformer(ValueTransformer):
    def __init__(self, data):
        super(GossFileModeTransformer, self).__init__(data)

    @property
    def transformed(self):
        value = self.data.get('value')
        if value in ['+x', 'executable']:
            return '0755'


class EchoTransformer(ValueTransformer):
    def __init__(self, data):
        super(EchoTransformer, self).__init__(data)

    @property
    def transformed(self):
        return self.data.get('value')
