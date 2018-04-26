import json
import tempfile

from docker.models.containers import Container
from jinja2 import TemplateError
from robot.libraries.BuiltIn import BuiltIn

from modules.ValidationTarget import ValidationTarget
from exc import ValidationError, DeploymentError
from tools.testutils import validate_context, validate_port, validate_property, validate_value, IpAddress, validate_matcher
from tools.GossTool import GossTool
from tools.goss.GossPort import GossPort


class Port(ValidationTarget):
    def __init__(self, instance=None):
        super(Port, self).__init__(instance)
        self.valid_contexts = ['service']
        self.properties = {
            'state': {
                'matchers': ['is', 'is not'],
                'values': ['open', 'closed']
            },
            'listening address': {
                'matchers': [],
                'value': IpAddress
            }
        }
        self.port = None
        self.protocol = 'tcp'
        self.transformed_data = None

    def validate(self):
        self._check_instance()
        self._check_data()
        validate_context(self.valid_contexts, self.instance.sut.target_type)
        (self.port, self.protocol) = validate_port(self.entity)
        self.property = validate_property(self.properties, self.property)
        validate_matcher([self.matcher], limit_to=self.properties.get('entity', {}).get('matchers', []))
        self.value = validate_value(self.properties, self.property, self.value)

    def transform(self):
        # create exchange format
        data = {
            'ports': [
                {
                    'port': self.port,
                    'protocol': self.protocol,
                    'state': self.value if 'state' in self.property else True,
                    'listening address': self.value if 'listening address' in self.property else []
                }
            ]
        }
        self.transformed_data = GossPort(data).transform()

    def run_test(self):
        self.validate()
        self.transform()

        # create gossfile on target container
        with tempfile.NamedTemporaryFile() as f:
            try:
                f.write(self.transformed_data)
                f.seek(0)

                # attach the goss volume to the service and update the SUT object
                container = self.instance.docker_controller.connect_volume_to_service(self.instance.sut.service_id, self.instance.test_volume)
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

        self.evaluate_results()

    def evaluate_results(self):
        assert isinstance(self.test_result['summary']['failed-count'], int)

        actual_value = self.test_result['results'][0]['found']
        if self.test_result['summary']['failed-count'] > 0:
            BuiltIn().log_to_console(json.dumps(self.test_result, indent=4, sort_keys=True))
            raise ValidationError(
                'Port {}: {} {} {}, actual: {}'.format(
                    self.entity,
                    self.property,
                    self.matcher,
                    self.value,
                    actual_value)
            )
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
