from jinja2 import Environment
from robot.libraries.BuiltIn import BuiltIn
from tools.goss.GossEntity import GossEntity


class GossPort(GossEntity):
    template = \
        """port:
            {% for port in ports %}
              {{ port.protocol or 'tcp' }}:{{ port.port }}:
                listening: {{ port.listening }}
                {% if port.ip %}ip: 
                {% for ip in port.ip %} - {{ ip }} {% endfor %}
                {% endif %}
        {% endfor %}"""
    key_mappings = {
        'state': 'listening',
        'listening address': 'ip'
    }
    type_mappings = {
        'ip': []
    }
    value_mappings = {
        'listening': {
            'open': True,
            'closed': False
        },
        'ip': {}
    }

    def __init__(self, data):
        GossEntity.__init__(self, data)
        self.name = 'ports'

    def transform(self):
        self.apply_mappings()

        self.out = Environment().from_string(self.template).render(self.mapped)
        BuiltIn().log_to_console('\n{}'.format(self.out))

        return self.out

    def apply_mappings(self):
        entities = self.mapped.get(self.name)
        assert isinstance(entities, list), 'entities is no list'

        for entity in entities:
            self._map(entity, self.key_mappings, self.type_mappings, self.value_mappings)

        return self.mapped


