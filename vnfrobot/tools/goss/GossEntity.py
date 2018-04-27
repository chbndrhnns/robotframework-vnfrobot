import copy
from abc import ABCMeta, abstractmethod

from exc import TransformationError


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

    def _map(self, entity, key_mappings=None, type_mappings=None, value_mappings=None, matcher_mappings=None):
        key_mappings = key_mappings if key_mappings else {}
        type_mappings = type_mappings if type_mappings else {}
        value_mappings = value_mappings if value_mappings else {}
        matcher_mappings = matcher_mappings if matcher_mappings else {}

        inverse_key_mappings = {v: k for k, v in key_mappings.iteritems()}
        keys = entity.keys()
        assert isinstance(self.inp, dict)
        assert isinstance(self.mapped, dict)
        assert self.inp == self.mapped
        keys_replaced = []

        try:
            self._create_new_keys(entity, key_mappings, keys, keys_replaced)
        except (AttributeError, TypeError, ValueError) as exc:
            raise TransformationError('create new keys: {}'.format(exc))

        try:
            self._create_new_types(entity, type_mappings)
        except (AttributeError, TypeError, ValueError) as exc:
            raise TransformationError('create new types: {}'.format(exc))

        for new_key, mapping in value_mappings.iteritems():
            old_key = inverse_key_mappings.get(new_key)
            if old_key in entity:
                try:
                    self._create_new_values(entity, matcher_mappings, new_key, old_key, value_mappings)
                except (AttributeError, ValueError, TypeError) as exc:
                    raise TransformationError('map values: {} - {}'.format(new_key, exc))

        for key in keys_replaced:
            if entity.get(key):
                del entity[key]

        return entity

    @staticmethod
    def _create_new_values(entity, matcher_mappings, new_key, old_key, value_mappings):
        # get matcher mapping
        matcher_mapping = matcher_mappings.get(new_key, {})
        old_matcher = entity.get(old_key, {}).get('matcher', None)
        new_matcher = matcher_mapping.get(old_matcher, None)
        # replace old value with new value
        if value_mappings.get(new_key, {}):
            if isinstance(entity[new_key], list):
                entity[new_key].append(value_mappings.get(new_key, {}).get(entity, None))
            else:
                old_val = entity.get(new_key, {}).get('value', None)

                if not new_matcher:
                    entity[new_key] = value_mappings.get(new_key, {}).get(old_val)
        # use old value
        else:
            if isinstance(entity[new_key], list) and len(entity[old_key]) > 0:
                entity[new_key].append(entity.get(old_key, {}).get('value'))
            else:
                entity[new_key] = entity.get(new_key)

    @staticmethod
    def _create_new_types(entity, type_mappings):
        for new_key, t in type_mappings.iteritems():
            if new_key in entity.keys():
                entity[new_key] = []

    @staticmethod
    def _create_new_keys(entity, key_mappings, keys, keys_replaced):
        for old_key, new_key in key_mappings.iteritems():
            if old_key in keys:
                entity[new_key] = entity[old_key]
                keys_replaced.append(old_key)
