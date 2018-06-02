from abc import ABCMeta, abstractmethod, abstractproperty

from docker.models.containers import Container
from docker.errors import APIError
from robot.libraries.BuiltIn import BuiltIn

from InfrastructureController import InfrastructureController
from exc import SetupError, ValidationError, NotFoundError, DeploymentError
from settings import Settings, set_breakpoint
from testtools.GossTool import GossTool
from testtools.TestTool import TestTool
from tools.data_structures import SUT
from tools.orchestrator import Orchestrator


class ValidationTarget:
    __metaclass__ = ABCMeta

    def __init__(self, instance=None):
        self.instance = instance
        self._test_results = None

        self.entity = None
        self.property = None
        self.matcher = None
        self.value = None

        self.data = {}
        self.transformed_data = {}

        assert isinstance(self.instance.orchestrator, Orchestrator)
        assert isinstance(self.instance.orchestrator.controller, InfrastructureController)

    @abstractproperty
    def options(self):
        raise NotImplementedError('must be implemented by the subclass')

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
    def _prepare_transform(self):
        raise NotImplementedError('must be implemented by the subclass')

    @abstractmethod
    def _prepare_run(self, tool_instance):
        raise NotImplementedError('must be implemented by the subclass')

    def transform(self):
        if self.options.get('transformation_handler'):
            if not self.data:
                self._prepare_transform()
            handler = self.options.get('transformation_handler', None)
            assert handler, 'ValidationTarget:transform_to_goss() expects a ' \
                            'class instance for the transformation handler'
            self.transformed_data = handler(self.data).transform_to_goss(handler)
            return self.transformed_data

    def run_test(self):
        if self.instance.fatal_error:
            raise ValidationError('We do not start validation as a fatal error occured during test setup.')

        if not self.instance.sut.target_type:
            raise ValidationError('No context given. Context must be set with "Set <context_type> context to <target>.')

        # set a flag to indicate that we at least tried to execute a test
        self.instance.validation_attempted = True

        # override sidecar decision for network context
        if 'network' in self.instance.sut.target_type:
            self.options['sidecar_required'] = True
            self.options['test_volume_required'] = True

        test_volume_required = self.options.get('test_volume_required', False)
        sidecar_required = self.options.get('sidecar_required', False)

        try:
            self.validate()
            self._prepare_transform()
            self.transform()
        except (ValidationError, NotFoundError, DeploymentError) as exc:
            self._cleanup()
            raise exc

        try:
            self.instance.orchestrator.get_or_create_deployment()
        except (ValidationError, NotFoundError, DeploymentError) as exc:
            self._cleanup()
            raise exc

        try:
            if test_volume_required:
                self._create_test_volume()
            if sidecar_required:
                sidecar_command = self.options.get('sidecar_command', None)
                self._create_sidecar(command=sidecar_command)
            if not sidecar_required and test_volume_required:
                self._connect_volume_to_sut()
            tool_instance = self.options.get('test_tool', None)(
                controller=self.instance.orchestrator.controller,
                sut=self.instance.sut
            )
            self._prepare_run(tool_instance)
            tool_instance.command = self.options.get('command', None) or tool_instance.command
        except (ValidationError, NotFoundError, DeploymentError) as exc:
            self._cleanup()
            raise exc

        try:
            # set_breakpoint()
            tool_instance.run(self)
        except (ValidationError, NotFoundError, DeploymentError) as exc:
            raise exc
        finally:
            self._cleanup()

        try:
            self.evaluate_results(tool_instance)
        except ValidationError as exc:
            raise exc

    def _create_sidecar(self, command=None):
        if not command:
            command = GossTool(controller=self.instance.orchestrator.controller).command
        network_name = self.instance.sut.service_id
        assert self.instance.orchestrator.controller.get_network(
            network_name), '_create_sidecar: cannot find network {}'.format(network_name)
        volumes = {
            self.instance.test_volume: {
                'bind': '/goss',
                'mode': 'ro'
            }
        }
        self.instance.sidecar = self.instance.orchestrator.controller.get_or_create_sidecar(
            name='robot_sidecar_for_{}'.format(self.instance.deployment_name),
            command=command,
            network=network_name,
            volumes=volumes)
        self.instance.update_sut(target_type='container', target=self.instance.sidecar.name)
        assert network_name in self.instance.sidecar.attrs['NetworkSettings']['Networks'].keys()

    def _connect_volume_to_sut(self):
        container = self.instance.orchestrator.controller.connect_volume_to_service(
            service=self.instance.sut.service_id,
            volume=self.instance.test_volume)
        assert isinstance(container, Container)
        self.instance.update_sut(target=container.name)

    def _create_test_volume(self):
        self.instance.test_volume = self.instance.orchestrator.check_or_create_test_tool_volume(
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
            raise ValidationError('Checking test data: No value supplied for {}'.format(missing))

    def _cleanup(self):
        if self.instance.sidecar:
            BuiltIn().log('Cleanup sidecar: removing {}'.format(self.instance.sidecar.name),
                          level='INFO',
                          console=Settings.to_console)
            assert isinstance(self.instance.sidecar, Container)
            try:
                self.instance.sidecar.kill()
            except APIError:
                pass

            try:
                self.instance.sidecar.remove()
            except APIError as exc:
                if 'No such container' not in exc.explanation:
                    BuiltIn().log('Cleanup failed: could not remove {}: exc'.format(self.instance.sidecar.name, exc),
                                  level='ERROR',
                                  console=Settings.to_console)
            self.instance.sidecar = None
