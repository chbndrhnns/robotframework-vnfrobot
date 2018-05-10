from ValidationTargets.ValidationTarget import ValidationTarget
from testtools.DockerTool import DockerTool
from tools import validators, matchers
from tools.testutils import call_validator


class Variable(ValidationTarget):
    options = {
        'test_tool': DockerTool,
        'command': 'env_vars'
    }

    properties = {
        'entity': {
            'matchers': matchers.all_matchers.keys(),
            'value': '[^\s]'
        }
    }

    allowed_contexts = ['service']
    entity_matcher = '[A-Z][A-Z0-9_]'

    def __init__(self, instance=None):
        super(Variable, self).__init__(instance)
        self.context_validator = validators.Context(['service'])

    def validate(self):
        self.property = self.entity if not self.property else self.property

        self._find_robot_instance()
        self._check_test_data()
        call_validator(self.instance.sut.target_type, validators.Context, Variable.allowed_contexts)
        call_validator(self.entity, validators.Regex, Variable.entity_matcher)
        call_validator(self.matcher, validators.InList, Variable.properties.get('entity', {}).get('matchers'))
        call_validator(self.value, validators.Regex, Variable.properties.get('entity', {}).get('value'))

    def _prepare_transform(self):
        pass

    def _prepare_run(self, tool_instance):
        pass
