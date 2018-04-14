import copy
from abc import ABCMeta, abstractmethod


class GossEntity():
    """
        contract:

        data = { 'ports': [
                            {
                            'port': 12345,
                            'state': 'open',
                            'listening address': '127.0.0.1'
                            }
                        ]
                }
    """
    __metaclass__ = ABCMeta

    def __init__(self, data):
        self.inp = data
        self.mapped = copy.deepcopy(data)
        self.out = None

    @abstractmethod
    def transform(self):
        """
        transform the test data into the yaml format that is understood by goss.

        Returns: dict - with mappings applied

        """
        pass

    @abstractmethod
    def apply_mappings(self):
        """
        apply_mappings applies test-tool specific changes to the input data by iterating over
        properties and values to replace matches.

        Returns: dict - with mappings applied

        """

        pass