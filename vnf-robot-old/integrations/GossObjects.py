import hashlib
from abc import ABCMeta, abstractmethod
from string import lower


class GossObject:
    __metaclass__ = ABCMeta

    required_attributes = None
    optional_attributes = None
    type = None
    destination = None

    def __init__(self):
        if self.type is None:
            raise NotImplementedError('type must be implemented.')
        if self.destination is None:
            raise NotImplementedError('destination must be implemented.')
        if self.required_attributes is None:
            raise NotImplementedError('required_attributes must be implemented.')
        if self.optional_attributes is None:
            raise NotImplementedError('optional_attributes must be implemented.')

    @abstractmethod
    def set_destination(self, attrs):
        raise NotImplementedError('{__name__} must be implemented.'.format(**self.__dict__))

    @abstractmethod
    def set_required_attributes(self, attrs):
        raise NotImplementedError('{__name__} must be implemented.'.format(**self.__dict__))

    def _generate_yaml(self):
        yaml = [ {self.type: self.destination }]
        yaml[self.type][self.destination].extend(self.required_attributes)
        yaml[self.type][self.destination].extend(self.required_attributes)

    def get_yaml(self):
        raise NotImplementedError('{__name__} must be implemented.'.format(**self.__dict__))


class GossFile(GossObject):
    def set_destination(self, dst):
        self.sut = dst

    def get_yaml(self):
        pass


    def __init__(self):
        self.type = lower(self.__class__.__name__)
        self.required_attributes = [{'exists': bool}]
        self.optional_attributes = [{'mode': unicode,
                                     'size': int,
                                     'owner': unicode,
                                     'group': unicode,
                                     'filetype': ['file', 'symlink', 'directory'],
                                     'contains': [str],
                                     'md5': hashlib.md5,
                                     'sha256': hashlib.sha256,
                                     'linked-to': str}]


    def set_required_attributes(self, attrs):
        pass
