from tools.goss import transformers
from tools.goss.GossEntity import GossEntity


class GossFile(GossEntity):
    name = 'files'
    template = \
        """file:
            {% for f in files %}
              {{ f.file }}:
                exists: {{ f.exists }}{% if f.mode %}
                mode: "{{ f.mode }}"{% endif %}{% if f.contains %}
                contains: 
                - "{{ f.contains }}"
                {% endif %}
            {% endfor %}
        """
    key_mappings = {
        'state': 'exists',
        'mode': 'mode',
        'content': 'contains'
    }
    type_mappings = {}
    value_mappings = {
        'exists': {
            'existing': True,
            'is not existing': False,
        },
        'mode': transformers.GossFileModeTransformer,
        'contains': transformers.EchoTransformer
    }
    matcher_mappings = {
        'existing': {
            'is': True,
            'is not': False
        }
    }

    def __init__(self, data):
        GossEntity.__init__(self, data)
