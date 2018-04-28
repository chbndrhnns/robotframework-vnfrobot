from ValidationTargets.ValidationTarget import ValidationTarget
from exc import NotFoundError, ValidationError
from tools.testutils import validate_context, validate_against_regex, get_truth, string_matchers


class Placement(ValidationTarget):
    """
    Set deployment context

    Ideas:
    - has networks
    - placement of sut: node.id is
    - placement of sut: node.hostname is
    - placement of sut: node.role is
    - placement of sut: node.labels contain

    """
    def __init__(self, instance=None):
        super(Placement, self).__init__(instance)
        self.valid_contexts = ['deployment']
        self.entity_matcher = '[a-zA-Z0-9_-]'
        self.value_matcher = '[^\s]'

    def validate(self):
        self.property = self.entity if not self.property else self.property

        self._check_instance()
        self._check_data()
        validate_context(self.valid_contexts, self.instance.sut.target_type)
        validate_against_regex('variable', self.entity, self.entity_matcher)
        validate_against_regex('value', self.value, self.value_matcher)

    def transform(self):
        pass

    def run_test(self):
        self.validate()
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
                'Variable {}: {} {}, actual: {}'.format(
                    self.entity,
                    self.matcher,
                    self.value,
                    self.test_result[0])
            )