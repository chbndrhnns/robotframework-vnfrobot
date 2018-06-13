from tools.goss.GossEntity import GossEntity


class GossPort(GossEntity):
    """
    Goss test: `port`

    """

    name = 'ports'
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
    matcher_mappings = {
        'listening': {
            'is': None,
            'is not': None
        },
        'ip': {}
    }

    def __init__(self, data):
        GossEntity.__init__(self, data)

