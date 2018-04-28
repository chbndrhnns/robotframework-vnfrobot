from ValidationTargets.ValidationTarget import ValidationTarget
from exc import NotFoundError, ValidationError
from tools import validators
from tools.testutils import get_truth, call_validator
from tools.matchers import string_matchers
from tools.validators import Service


class Placement(ValidationTarget):
    """
    Set service context

    # Ideas:
    - placement: node.id is
    - placement: node.hostname is
    - placement: node.role is
    - placement: node.labels contain

    """

    properties = {
        'node.id': {
            'matchers': ['is', 'is not'],
            'value': '\S+'
        },
        'node.role': {
            'matchers': ['contains', 'contains not', 'is', 'is not'],
            'value': '\S+'
        },
        'node.hostname': {
            'matchers': ['contains', 'contains not', 'is', 'is not'],
            'value': '\S+'
        },
        'node.labels': {
            'matchers': ['contains', 'contains not', 'is', 'is not'],
            'value': '\S+'
        }
    }
    allowed_contexts = ['service']

    def __init__(self, instance=None):
        super(Placement, self).__init__(instance)

    def validate(self):
        self._find_robot_instance()
        self._check_test_data()

        call_validator(self.instance.sut.target_type, validators.Context, Placement.allowed_contexts)
        call_validator(self.property, validators.Property, Placement.properties)
        call_validator(self.matcher, validators.InList, Placement.properties.get(self.property, {}).get('matchers', []))
        call_validator(self.value, validators.Regex, Placement.properties.get(self.property, {}).get('value', ''))

    def transform(self):
        pass

    def run_test(self):
        try:
            self.validate()
        except ValidationError as exc:
            raise
        try:
            env = self.instance.docker_controller.get_env(self.instance.sut.service_id)
            self.test_result = [e.split('=')[1] for e in env if self.entity == e.split('=')[0]]
        except NotFoundError:
            raise

        self.evaluate_results()

    def evaluate_results(self):
        if not self.test_result:
            raise ValidationError('No variable {} found.'.format(self.entity))

        if not get_truth(self.test_result[0], string_matchers[self.matcher], self.value):
            raise ValidationError(
                'Placement: {} {}, actual: {}'.format(
                    self.matcher,
                    self.value,
                    self.test_result[0])
            )

    def get_as_dict(self):
        return {
            'context': getattr(self, 'context', None),
            'property': getattr(self, 'property', None),
            'matcher': getattr(self, 'matcher', None),
            'value': getattr(self, 'value', None)
        }
