import json
import tempfile

from ValidationTargets.ValidationTarget import ValidationTarget
from exc import ValidationError, SetupError, DeploymentError
from settings import Settings
from tools import testutils, validators, orchestrator
from tools.GossTool import GossTool
from tools.goss.GossAddr import GossAddr
from tools.testutils import validate_matcher, validate_value, call_validator
from tools.validators import Domain


class Address(ValidationTarget):
    properties = {
        'entity': {
            'matchers': ['is', 'is not'],
            'values': ['reachable']
        }
    }

    def __init__(self, instance=None):
        super(Address, self).__init__()
        self.context_validator = validators.Context
        self.allowed_contexts = ['service', 'network']
        self.transformed_data = {}
        self.port = None
        self.address = None
        self.instance = instance

    def validate(self):
        self.property = self.entity if not self.property else self.property

        try:
            self._find_robot_instance()
            self._check_test_data()
            call_validator(self.instance.sut.target_type, self.context_validator, self.allowed_contexts)

            call_validator(self.matcher, validators.InList, Address.properties.get('entity', {}).get('matchers', []))
            call_validator(self.value, validators.InList, Address.properties.get('entity', {}).get('values', []))

            # split address in case a port is given
            split_entity = self.entity.split(':')
            if len(split_entity) > 2:
                raise ValidationError('Value "{}" is invalid.'.format(self.entity))
            self.address = split_entity[0]
            self.port = split_entity[1] if len(split_entity) == 2 else '80'
            call_validator(self.address, validators.Domain)
            call_validator(self.port, validators.Port)
        except (SetupError, ValidationError) as exc:
            raise



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
        try:
            self.validate()
            self.transform()

            orchestrator.get_or_create_deployment(self.instance)
            self.instance.test_volume = orchestrator.get_or_create_test_tool_volume(
                self.instance.docker_controller,
                Settings.goss_helper_volume
            )
        except (ValidationError, DeploymentError) as exc:
            raise exc

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
                raise DeploymentError('Could not run test tool on {}: {}'.format(self.instance.sut, exc))

        testutils.evaluate_results(self)