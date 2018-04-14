from jinja2 import Environment
from robot.libraries.BuiltIn import BuiltIn

from tools.goss.GossEntity import GossEntity


class GossPort(GossEntity):
    template = \
        """port:
            {% for port in ports %}
              {{ port.protocol or 'tcp' }}:{{ port.port }}:
                listening: {{ port.listening }}
                {% if port.addresses %}ip: 
                {% for ip in port.addresses %} - {{ ip }} {% endfor %}
                {% endif %}
        {% endfor %}
        """

    def __init__(self, data):
        GossEntity.__init__(self, data)

    def transform(self):
        self.apply_mappings()

        self.out = Environment().from_string(self.template).render(self.mapped)
        BuiltIn().log_to_console('\n{}'.format(self.out))

        return self.out

    def apply_mappings(self):
        key_mappings = {
            'state': 'listening',
            'listening address': 'ip'
        }
        value_mappings = {
            'listening': {
                'open': 'true',
                'closed': 'false'
            }
        }

        entities = self.mapped.get('ports')
        assert isinstance(entities, list), 'entities is no list'

        for idx, val in enumerate(entities):

            assert isinstance(self.inp, dict)
            assert isinstance(self.mapped, dict)
            assert self.inp == self.mapped

            for k in key_mappings:
                new_key = key_mappings.get(k, None)
                old_key = k
                if old_key in entities[idx].keys():
                    entities[idx][new_key] = entities[idx].get(old_key, None)
                    del entities[idx][old_key]

            for k in value_mappings:
                assert entities[idx].get(k, False)
                old_val = entities[idx].get(k, False)
                assert old_val
                entities[idx][k] = value_mappings.get(k, {}).get(old_val)

        return self.mapped