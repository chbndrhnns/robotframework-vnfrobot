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

    def _map(self, entity, key_mappings=None, type_mappings=None, value_mappings=None):
        if key_mappings is None:
            key_mappings = {}
        if type_mappings is None:
            type_mappings = {}
        if value_mappings is None:
            value_mappings = {}

        inverse_key_mappings = {v: k for k, v in key_mappings.iteritems()}
        keys = entity.keys()
        assert isinstance(self.inp, dict)
        assert isinstance(self.mapped, dict)
        assert self.inp == self.mapped
        keys_replaced = []

        # create new keys, remove old keys
        for old_key, new_key in key_mappings.iteritems():
            if old_key in keys:
                entity[new_key] = entity[old_key]
                keys_replaced.append(old_key)

        # create new types of values if necessary
        for new_key, t in type_mappings.iteritems():
            if new_key in entity.keys():
                entity[new_key] = []

        for new_key, mapping in value_mappings.iteritems():
            old_key = inverse_key_mappings.get(new_key)
            if old_key in entity:

                # replace old value with new value
                if value_mappings.get(new_key):
                    if isinstance(entity[new_key], list):
                        entity[new_key].append(value_mappings.get(new_key, {}).get(entity, None))
                    else:
                        old_val = entity.get(new_key, None)
                        entity[new_key] = value_mappings.get(new_key, {}).get(old_val)
                # use old value
                else:
                    if isinstance(entity[new_key], list) and len(entity[old_key]) > 0:
                        entity[new_key].append(entity.get(old_key))
                    else:
                        entity[new_key] = entity.get(new_key)
        for key in keys_replaced:
            del entity[key]

        return entity
