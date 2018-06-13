from abc import ABCMeta, abstractproperty


class ValueTransformer:
    """
    Base class for value transformer subclasses. Used to transform a value for the use with a test tool.

    """
    __metaclass__ = ABCMeta

    def __init__(self, data):
        self.data = data
        assert self.data, 'Cannot instantiate ValueTransformer class without providing data.'

    @abstractproperty
    def transformed(self):
        """
        Returns the transformed value

        Returns:
            val

        """
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
