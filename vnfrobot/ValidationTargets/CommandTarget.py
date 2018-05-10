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
            'value': String
        },
        'stdout': {
            'matchers': ['is', 'is not', 'contains', 'contains not'],
            'value': String
        },
        'stderr': {
            'matchers': ['is', 'is not', 'contains', 'contains not'],
            'value': String
        },
    }
    options = {
        'test_tool': DockerTool,
        'command': 'run_in_container'
    }
    allowed_contexts = ['service', 'network']

    def __init__(self, instance=None):
        super(Command, self).__init__(instance)

    def validate(self):
        self._find_robot_instance()
        self._check_test_data()

        call_validator(self.instance.sut.target_type, validators.Context, Command.allowed_contexts)
        call_validator(self.property, validators.Property, Command.properties)
        call_validator(self.matcher, validators.InList, Command.properties.get(self.property, {}).get('matchers', []))
        validate_value(Command.properties, self.property, self.value)

    def _prepare_transform(self):
        self.options['sidecar_command'] = self.entity

    def _prepare_run(self, tool_instance):
        pass
