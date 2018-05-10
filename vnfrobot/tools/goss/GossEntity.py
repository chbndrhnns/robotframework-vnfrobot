import copy
from abc import ABCMeta

from jinja2 import Environment
from robot.libraries.BuiltIn import BuiltIn

from exc import TransformationError
from settings import Settings


class GossEntity:
    __metaclass__ = ABCMeta

    template = "__not_for_use__"
    key_mappings = {}
    type_mappings = {}
    value_mappings = {}
    matcher_mappings = {}

    def __init__(self, data):
        self.inp = data
        self.mapped = copy.deepcopy(data)
        self.out = None

    def transform(self, entity):
        """
        Transform the test data into the yaml format that is understood by goss.

        Returns: dict - with mappings applied

        """
        self.apply_mappings(entity)

        self.out = Environment().from_string(entity.template).render(self.mapped)
        BuiltIn().log('\n{}'.format(self.out), level='DEBUG', console=Settings.to_console)

        return self.out

    def apply_mappings(self, goss_entity):
        """
        Apply test-tool specific changes to the input data by iterating over
        properties and values to replace matches.

        Returns: dict - with mappings applied

        """
        entities = self.mapped.get(goss_entity.name)
        assert isinstance(entities, list), 'entities is no list'

        for entity in entities:
            try:
                self._map(entity, goss_entity.key_mappings, goss_entity.type_mappings, goss_entity.value_mappings,
                          goss_entity.matcher_mappings)
            except (AttributeError, TypeError, ValueError) as exc:
                raise TransformationError('apply_mappings: {}'.format(exc))

        return self.mapped

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
        matcher_mapping = matcher_mappings.get(new_key, {})
        old_matcher = entity.get(old_key, {}).get('matcher', None)
        new_matcher = matcher_mapping.get(old_matcher, None)
        # replace old value with new value if a mapping exists
        if value_mappings.get(new_key, {}):
            if isinstance(entity[new_key], list):
                entity[new_key].append(value_mappings.get(new_key, {}).get(entity, None))
            else:
                old_val = entity.get(new_key, {}).get('value', None)

                if new_matcher is None:
                    entity[new_key] = value_mappings.get(new_key, {}).get(old_val)
                elif isinstance(new_matcher, bool):
                    entity[new_key] = new_matcher
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
