import json
import tempfile

from robot.libraries.BuiltIn import BuiltIn

from modules.ValidationTarget import ValidationTarget
from exc import ValidationError, SetupError, DeploymentError
from tools import testutils
from tools.GossTool import GossTool
from tools.goss.GossAddr import GossAddr
from tools.testutils import validate_context, validate_matcher, validate_value, validate_entity, Domain


class Address(ValidationTarget):
    properties = {
        'entity': {
            'matchers': ['is', 'is not'],
            'values': ['reachable']
        }
    }

    def __init__(self, instance=None):
        super(Address, self).__init__()
        self.valid_contexts = ['service', 'network']

        self.entity_matcher = Domain
        self.transformed_data = {}
        self.port = None
        self.address = None
        self.instance = instance

    def validate(self):
        self.property = self.entity if not self.property else self.property

        try:
            self._check_instance()
            self._check_data()
            validate_context(self.valid_contexts, self.instance.sut.target_type)
            validate_entity(self.entity, self.entity_matcher)
            validate_matcher([self.matcher], limit_to=Address.properties.get('entity', {}).get('matchers', []))
            validate_value(Address.properties, 'entity', self.value)
        except (SetupError, ValidationError) as exc:
            raise

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
                    'state': {
                        'matcher': self.matcher,
                        'value': self.value
                    },
                }
            ]
        }
        entity = GossAddr(data)
        self.transformed_data = entity.transform(entity)

    def run_test(self):
        self.validate()
        self.transform()

        # create gossfile on target container
        with tempfile.NamedTemporaryFile() as f:
            try:
                f.write(self.transformed_data)
                f.seek(0)

                # create sidecar
                network_name = self.instance.sut.target
                volumes = {
                    self.instance.test_volume: {
                        'bind': '/goss',
                        'mode': 'ro'
                    }
                }
                sidecar = self.instance.docker_controller.get_or_create_sidecar(
                    name='robot_sidecar_for_{}'.format(self.instance.deployment_name),
                    command=GossTool(controller=self.instance.docker_controller).command,
                    network=network_name,
                    volumes=volumes)
                assert network_name in sidecar.attrs['NetworkSettings']['Networks'].keys()

                self.instance.docker_controller.put_file(entity=sidecar, file_to_transfer=f.name,
                                                         filename='goss.yaml')

                res = self.instance.docker_controller.run_sidecar(sidecar=sidecar)
                self.test_result = json.loads(res)
            except (TypeError, ValueError) as exc:
                raise ValidationError('ValidationError: {}'.format(exc))
            except DeploymentError as exc:
                raise DeploymentError('Could not run test tool on {}'.format(self.instance.sut))

        testutils.evaluate_results(self)