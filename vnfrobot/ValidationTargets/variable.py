from ValidationTargets.ValidationTarget import ValidationTarget
from exc import NotFoundError, ValidationError
from tools import validators, matchers
from tools.testutils import validate_against_regex, get_truth, call_validator
from tools.matchers import string_matchers


class Variable(ValidationTarget):
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

    def transform(self):
        pass

    def run_test(self):
        try:
            self.validate()
            env = self.instance.docker_controller.get_env(self.instance.sut.service_id)
            self.test_result = [e.split('=')[1] for e in env if self.entity == e.split('=')[0]]
        except (NotFoundError, ValidationError):
            raise

        self.evaluate_results()

    def evaluate_results(self):
        if not self.test_result:
            raise ValidationError('No variable {} found.'.format(self.entity))

        if not get_truth(self.test_result[0], string_matchers[self.matcher], self.value):
            raise ValidationError(
                'Variable {}: {} {}, actual: {}'.format(
                    self.entity,
                    self.matcher,
                    self.value,
                    self.test_result[0])
            )