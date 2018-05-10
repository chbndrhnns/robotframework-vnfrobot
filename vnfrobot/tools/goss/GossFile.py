from tools.goss.GossEntity import GossEntity


class GossFile(GossEntity):
    name = 'files'
    template = \
        """file:
            {% for f in files %}
              {{ f.file }}:
                exists: {{ f.exists }}
            {% endfor %}
        """
    key_mappings = {
        'state': 'exists'
    }
    type_mappings = {}
    value_mappings = {
        'exists': {
            'existing': True,
            'is not existing': False,
        }
    }
    matcher_mappings = {
        'existing': {
            'is': True,
            'is not': False
        }
    }

    def __init__(self, data):
        GossEntity.__init__(self, data)
