from ValidationTargets.ValidationTarget import ValidationTarget
from testtools.DockerTool import DockerTool
from tools import validators, matchers
from tools.testutils import call_validator, validate_value
from tools.validators import String


class Command(ValidationTarget):
    """
    Run a command in a service

    """
    properties = {
        'return code': {
            'matchers': matchers.number_matchers.keys(),
            'values': String
        },
        'stdout': {
            'matchers': ['is', 'is not', 'contains', 'contains not', 'is empty', 'is not empty'],
            'values': String
        },
        'stderr': {
            'matchers': ['is', 'is not', 'contains', 'contains not', 'is empty', 'is not empty'],
            'values': String
        },
    }
    allowed_contexts = ['service', 'network']

    def __init__(self, instance=None):
        super(Command, self).__init__(instance)

        self.options = {
            'test_tool': DockerTool,
            'command': 'run_in_container',
            'sidecar_required': False,
        }

    def validate(self):
        self._find_robot_instance()
        self._check_test_data()

        call_validator(self.instance.sut.target_type, validators.Context, Command.allowed_contexts)
        call_validator(self.property, validators.Property, Command.properties)
        if 'empty' in self.value:
            if 'is' in self.matcher or 'is not' in self.matcher:
                self.matcher = '{} {}'.format(self.matcher, self.value)
                self.value = None

        call_validator(self.matcher, validators.InList, Command.properties.get(self.property, {}).get('matchers', []))
        if 'empty' not in self.matcher:
            validate_value(Command.properties, self.property, self.value)

    def _prepare_transform(self):
        self.options['sidecar_command'] = self.entity

    def _prepare_run(self, tool_instance):
        pass
