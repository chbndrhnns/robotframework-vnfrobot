from abc import ABCMeta, abstractmethod, abstractproperty

from docker.models.containers import Container
from docker.errors import APIError
from robot.libraries.BuiltIn import BuiltIn

from exc import SetupError, ValidationError, NotFoundError
from settings import Settings
from testtools.GossTool import GossTool
from testtools.TestTool import TestTool
from tools import orchestrator
from tools.data_structures import SUT


class ValidationTarget:
    __metaclass__ = ABCMeta

    def __init__(self, instance=None):
        self.instance = instance
        self._test_results = None

        self.entity = None
        self.property = None
        self.matcher = None
        self.value = None

    @abstractproperty
    def options(self):
        pass

    @property
    def test_results(self):
        return self._test_results

    @test_results.setter
    def test_results(self, value):
        self._test_results = value

    def get_as_dict(self):
        return {
            'context': getattr(self, 'context', None),
            'entity': getattr(self, 'entity', None),
            'property': getattr(self, 'property', None),
            'matcher': getattr(self, 'matcher', None),
            'value': getattr(self, 'value', None)
        }

    def get(self, prop):
        return getattr(self, prop, None)

    def set(self, prop, value):
        try:
            if isinstance(value, basestring):
                value = value.strip('"\'\n')
            setattr(self, prop, unicode(value))
        except AttributeError:
            raise

    def set_as_dict(self, data=None):
        if data is None:
            data = {}

        for key, val in data.iteritems():
            try:
                self.set(key, val)
            except AttributeError:
                raise

    @abstractmethod
    def validate(self):
        pass

    @abstractmethod
    def transform(self):
        pass

    @abstractmethod
    def _prepare_run(self, tool_instance):
        pass

    def run_test(self, command=None):
        test_volume_required = self.options.get('test_volume_required', False)
        sidecar_required = self.options.get('sidecar_required', False)

        try:
            self.validate()
            self.transform()
            orchestrator.get_or_create_deployment(self.instance)
            if test_volume_required:
                self._create_test_volume()
            if sidecar_required:
                self._create_sidecar()
            if test_volume_required:
                self._connect_volume_to_sut()
            tool_instance = self.options.get('test_tool', None)(
                controller=self.instance.docker_controller,
                sut=self.instance.sut
            )
            self._prepare_run(tool_instance)
            tool_instance.command = self.options.get('command', None) or tool_instance.command
            tool_instance.run()
            self._cleanup()
        except (ValidationError, NotFoundError) as exc:
            raise exc

        try:
            self.evaluate_results(tool_instance)
        except ValidationError as exc:
            raise exc

    def _create_sidecar(self):
        network_name = self.instance.sut.target
        volumes = {
            self.instance.test_volume: {
                'bind': '/goss',
                'mode': 'ro'
            }
        }
        self.instance.sidecar = self.instance.docker_controller.get_or_create_sidecar(
            name='robot_sidecar_for_{}'.format(self.instance.deployment_name),
            command=GossTool(controller=self.instance.docker_controller).command,
            network=network_name,
            volumes=volumes)
        self.instance.update_sut(target=self.instance.sidecar.name)
        assert network_name in self.instance.sidecar.attrs['NetworkSettings']['Networks'].keys()

    def _connect_volume_to_sut(self):
        container = self.instance.docker_controller.connect_volume_to_service(self.instance.sut.service_id,
                                                                              self.instance.test_volume)
        assert isinstance(container, Container)
        self.instance.update_sut(target=container.name)

    def _create_test_volume(self):
        self.instance.test_volume = orchestrator.check_or_create_test_tool_volume(
            self.instance.docker_controller,
            Settings.goss_helper_volume
        )

    def evaluate_results(self, tool_instance):
        if not isinstance(tool_instance, TestTool):
            raise TypeError('evaluate_results must be called with an instance of TestTool.')
        tool_instance.process_results(self)

    def _find_robot_instance(self):
        if not self.instance:
            raise SetupError('No robot instance found.')
        if not isinstance(self.instance.sut, SUT):
            raise SetupError('No SUT declared.')

    def _check_test_data(self):
        missing = [key for key, value in self.get_as_dict().iteritems() if not value]
        if missing:
            raise ValueError('Checking test data: No value supplied for {}'.format(missing))

    def _cleanup(self):
        if self.instance.sidecar:
            BuiltIn().log('Cleanup sidecar: removing {}'.format(self.instance.sidecar.name),
                          level='DEBUG',
                          console=True)
            assert isinstance(self.instance.sidecar, Container)
            try:
                self.instance.sidecar.kill()
            except APIError:
                pass

            try:
                self.instance.sidecar.remove()
            except APIError as exc:
                if not 'No such container' in exc.explanation:
                    BuiltIn().log('Cleanup failed: could not remove {}: exc'.format(self.instance.sidecar.name, exc),
                                  level='ERROR',
                                  console=True)


