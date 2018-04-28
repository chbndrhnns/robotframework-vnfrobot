import tempfile

from docker.models.containers import Container
from jinja2 import TemplateError

from ValidationTargets.ValidationTarget import ValidationTarget
from exc import ValidationError, DeploymentError
from tools import testutils
from tools.testutils import validate_context, validate_port, validate_property, validate_value, IpAddress, \
    validate_matcher
from tools.GossTool import GossTool
from tools.goss.GossPort import GossPort


class Port(ValidationTarget):
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

    def __init__(self, instance=None):
        super(Port, self).__init__(instance)
        self.data = None
        self.valid_contexts = ['service']

        self.port = None
        self.protocol = 'tcp'
        self.transformed_data = None

    def validate(self):
        self._check_instance()
        self._check_data()
        validate_context(self.valid_contexts, self.instance.sut.target_type)
        (self.port, self.protocol) = validate_port(self.entity)
        self.property = validate_property(Port.properties, self.property)
        validate_matcher([self.matcher], limit_to=Port.properties.get('entity', {}).get('matchers', []))
        self.value = validate_value(Port.properties, self.property, self.value)

    def transform(self):
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
        self.transformed_data = g.transform(g)

    def run_test(self):
        self.validate()
        self.transform()

        # create gossfile on target container
        with tempfile.NamedTemporaryFile() as f:
            try:
                f.write(self.transformed_data)
                f.seek(0)

                # attach the goss volume to the service and update the SUT object
                container = self.instance.docker_controller.connect_volume_to_service(self.instance.sut.service_id,
                                                                                      self.instance.test_volume)
                assert isinstance(container, Container)
                self.instance.update_sut(target=container.name)

                self.instance.docker_controller.put_file(entity=self.instance.sut.target, file_to_transfer=f.name,
                                                         filename='goss.yaml')

                self.test_result = GossTool(
                    controller=self.instance.docker_controller,
                    sut=self.instance.sut,
                    gossfile='/goss.yaml'
                ).run()
            except (TemplateError, TypeError, ValueError) as exc:
                raise ValidationError('Could not transform the test data: {}'.format(exc))
            except DeploymentError as exc:
                raise DeploymentError('Could not run test tool on {}'.format(self.instance.sut))

        testutils.evaluate_results(self)
#
#
# class Matcher(Enum):
#     IS = 'is'
#     IS_NOT = 'is not'
#     EXISTS = 'exists'
#     EXISTS_NOT = 'exists not'
#     CONTAINS = 'contains'
#     CONTAINS_NOT = 'contains not'
#     HAS = 'has'
#     HAS_NOT = 'has not'
#     GREATER = 'greater'
#     GREATER_OR_EQUAL = 'greater or equal'
#     LESSER = 'lesser'
#     LESSER_OR_EQUAL = 'lesser or equal'
