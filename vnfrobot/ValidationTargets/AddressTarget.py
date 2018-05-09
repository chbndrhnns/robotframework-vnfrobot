from ValidationTargets.ValidationTarget import ValidationTarget
from exc import ValidationError, SetupError
from tools import validators
from testtools.GossTool import GossTool
from tools.goss.GossAddr import GossAddr
from tools.testutils import call_validator


class Address(ValidationTarget):
    properties = {
        'entity': {
            'matchers': ['is', 'is not'],
            'values': ['reachable']
        }
    }
    options = {
        'test_tool': GossTool,
        'test_volume_required': True
    }
    allowed_contexts = ['service', 'network']

    def __init__(self, instance=None):
        super(Address, self).__init__(instance)
        self.transformed_data = {}
        self.port = None
        self.address = None

    def validate(self):
        self.property = self.entity if not self.property else self.property

        try:
            self._find_robot_instance()
            self._check_test_data()
            call_validator(self.instance.sut.target_type, validators.Context, self.allowed_contexts)

            call_validator(self.matcher, validators.InList, Address.properties.get('entity', {}).get('matchers', []))
            call_validator(self.value, validators.InList, Address.properties.get('entity', {}).get('values', []))

            # split address in case a port is given
            split_entity = self.entity.split(':')
            if len(split_entity) > 2:
                raise ValidationError('Value "{}" is invalid.'.format(self.entity))
            self.address = split_entity[0]
            self.port = split_entity[1] if len(split_entity) == 2 else '80'
            call_validator(self.address, validators.Domain)
            call_validator(self.port, validators.Port)
        except (SetupError, ValidationError) as exc:
            raise exc

    def _prepare_run(self, tool_instance):
        tool_instance.inject_gossfile(self)

    def transform(self):
        # tcp: // ip - address - or -domain - name:80:
        # reachable: true
        # timeout: 500
        #
        # create exchange format

        data = {
            'addresses': [
                {
                    'port': self.port,
                    'protocol': 'tcp',
                    'address': self.address,
                    'state': {
                        'matcher': self.matcher,
                        'value': self.value
                    },
                }
            ]
        }
        entity = GossAddr(data)
        self.transformed_data = entity.transform(entity)

