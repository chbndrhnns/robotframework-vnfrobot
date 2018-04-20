from modules.ValidationTarget import ValidationTarget
from exc import NotFoundError, ValidationError
from tools.goss.GossAddr import GossAddr
from tools.testutils import Url, validate_context, validate_matcher, validate_value, get_truth, boolean_matchers, \
    validate_entity, Domain


class Address(ValidationTarget):
    def __init__(self, instance=None):
        super(Address, self).__init__(instance)
        self.valid_contexts = ['service', 'network']
        self.properties = {
            'entity': {
                'matchers': ['is', 'is not'],
                'values': ['reachable']
            }
        }
        self.entity_matcher = Domain
        self.transformed_data = {}
        self.port = None
        self.address = None

    def validate(self):
        self.property = self.entity if not self.property else self.property

        self._check_instance()
        self._check_data()
        validate_context(self.valid_contexts, self.instance.sut.target_type)
        validate_entity(self.entity, self.entity_matcher)
        validate_matcher([self.matcher], limit_to=self.properties.get('entity', {}).get('matchers', []))
        validate_value(self.properties, 'entity', self.value)

        split_entity = self.entity.split(':')
        self.address = split_entity[0]
        self.port = split_entity[1] if len(split_entity) == 2 else '80'

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
                    'state': '{} {}'.format(self.matcher, self.value),
                }
            ]
        }
        self.transformed_data = GossAddr(data).transform()

    def run_test(self):
        self.validate()
        self.transform()

        try:
            env = self.instance.docker_controller.get_env(self.instance.sut.service_id)
            self.test_result = [e.split('=')[1] for e in env if self.entity == e.split('=')[0]]
        except NotFoundError:
            raise

        self.evaluate_results()

    def evaluate_results(self):
        if not self.test_result:
            raise ValidationError('No variable {} found.'.format(self.entity))

        if not get_truth(self.test_result[0], boolean_matchers[self.matcher], self.value):
            raise ValidationError(
                'Variable {}: {} {}, actual: {}'.format(
                    self.entity,
                    self.matcher,
                    self.value,
                    self.test_result[0])
            )
