from ValidationTargets.ValidationTarget import ValidationTarget
from tools import validators
from tools.testutils import validate_port, validate_property, validate_value, validate_matcher, call_validator
from tools.validators import IpAddress
from testtools.GossTool import GossTool
from tools.goss.GossPort import GossPort


class Port(ValidationTarget):
    allowed_contexts = ['service']
    properties = {
        'state': {
            'matchers': ['is'],
            'values': ['open', 'closed']
        },
        'listening address': {
            'matchers': [],
            'value': IpAddress
        }
    }
    options = {
        'test_volume_required': True,
        'test_tool': GossTool,
        'transformation_handler': GossPort
    }

    def __init__(self, instance=None):
        super(Port, self).__init__(instance)
        self.data = None

        self.port = None
        self.protocol = 'tcp'
        self.transformed_data = None

    def validate(self):
        self._find_robot_instance()
        self._check_test_data()
        call_validator(self.instance.sut.target_type, validators.Service, Port.allowed_contexts)
        (self.port, self.protocol) = validate_port(self.entity)
        self.property = validate_property(Port.properties, self.property)
        validate_matcher([self.matcher], limit_to=Port.properties.get('entity', {}).get('matchers', []))
        self.value = validate_value(Port.properties, self.property, self.value)

    def _prepare_transform(self):
        # create exchange format
        self.data = {'ports': [{'port': self.port, 'protocol': self.protocol}]}
        port = self.data.get('ports', [])[0]
        port.update({
            self.property: {
                'matcher': self.matcher,
                'value': self.value,
            }})

        # add properties that are implicitly necessary
        if 'state' not in self.property:
            port.update({
                'state': {
                    'matcher': 'is',
                    'value': 'open',
                }})
        g = GossPort(self.data)
        self.transformed_data = g.transform_to_goss(g)

    def _prepare_run(self, tool_instance):
        tool_instance.inject_gossfile(self)

