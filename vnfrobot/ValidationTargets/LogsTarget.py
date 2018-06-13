from ValidationTargets.ValidationTarget import ValidationTarget
from testtools.DockerTool import DockerTool
from tools import validators, matchers
from tools.testutils import call_validator, validate_value
from tools.validators import String


class LogsTarget(ValidationTarget):
    """
    Retrieves log files for service

    """
    properties = {
        'entity': {
            'matchers': ['contains', 'contains not'],
            'values': validators.NonEmptyString
        }
    }

    allowed_contexts = ['service']

    def __init__(self, instance=None):
        super(LogsTarget, self).__init__(instance)
        self.options = {
            'test_tool': DockerTool,
            'command': 'logs'
        }

    def validate(self):
        self._find_robot_instance()
        # self._check_test_data()

        call_validator(self.instance.sut.target_type, validators.Context, LogsTarget.allowed_contexts)
        call_validator(self.matcher, validators.InList, LogsTarget.properties.get('entity', {}).get('matchers', []))
        call_validator(self.value, validators.NonEmptyString)

    def _prepare_transform(self):
        pass

    def _prepare_run(self, tool_instance):
        pass
