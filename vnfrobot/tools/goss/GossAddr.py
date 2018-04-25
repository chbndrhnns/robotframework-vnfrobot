from jinja2 import Environment
from robot.libraries.BuiltIn import BuiltIn

from tools.goss.GossEntity import GossEntity


class GossAddr(GossEntity):
    template = \
        """addr:
            {% for addr in addresses %}
              {{ addr.protocol or 'tcp' }}://{{ addr.address }}:{{ addr.port }}:
                reachable: {{ addr.reachable }}
                timeout: 1000
            {% endfor %}
        """
    key_mappings = {
        'state': 'reachable'
    }
    value_mappings = {
        'reachable': {
            'is reachable': True,
            'is not reachable': False,
        }
    }

    def __init__(self, data):
        GossEntity.__init__(self, data)
        self.name = 'addresses'

    def transform(self):
        self.apply_mappings()

        self.out = Environment().from_string(self.template).render(self.mapped)
        BuiltIn().log_to_console('\n{}'.format(self.out))

        return self.out

    def apply_mappings(self):
        entities = self.mapped.get(self.name)
        assert isinstance(entities, list), 'entities is no list'

        for entity in entities:
            self._map(entity, self.key_mappings, None, self.value_mappings)

        return self.mapped
