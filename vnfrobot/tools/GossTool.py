import json
from abc import ABCMeta, abstractmethod

from DockerController import DockerController
from exc import DeploymentError, TestToolError
from modules.context import SUT


class TestTool:
    __metaclass__ = ABCMeta

    def __init__(self, controller, context, sut):
        self.command = None
        self.controller = controller if isinstance(controller, DockerController) else None
        self.sut = sut if isinstance(sut, SUT) else None
        self.context = context if context else 'service'
        self.created_entities = []

    @abstractmethod
    def run(self):
        pass

    def _generate_sidecar_name(self):
        return 'robot_sidecar_for_{}'.format(self.sut.service_id)


class GossTool(TestTool):
    def __init__(self, controller=None, sut=None, gossfile='/goss.yaml', context='service'):
        TestTool.__init__(self, controller, context, sut)

        self.gossfile = gossfile
        self.command = '/goss/goss-linux-amd64 --gossfile /{} validate --format json'.format(self.gossfile)
        self.sidecar = None
        self.target = None

    def run(self):
        res = ''
        try:
            if not self.sut:
                raise AttributeError('Target is necessary to run goss.')
            if not self.controller:
                raise AttributeError('Controller is necessary to run goss.')

            self._prepare()
            res = self.controller.execute(self.target, self.command).strip()
            return json.loads(res)
        except (json.JSONDecoder, ValueError) as exc:
            if 'No help topic' in res:
                raise TestToolError('Syntax error while calling goss on {}: {}'.format(self.sut.target, res))
            elif 'File error: open' in res:
                raise TestToolError('Gossfile not found on {}: {}'.format(self.sut.target, self.gossfile))
            elif 'Error: yaml:' in res or 'invalid character' in res:
                raise TestToolError('Syntax errors in provided yaml file {}: {}'.format(self.gossfile, res))
            elif 'no such file or directory' in res or 'executable file not found in' in res:
                raise TestToolError('goss executable was not found on {}: {}'.format(self.sut.target, res))

            raise TestToolError('Could not parse return value from goss: {}'.format(res))
        except AttributeError as exc:
            raise TestToolError('Error: {}'.format(exc))
        except DeploymentError as exc:
            raise

    def _prepare(self):
            if self.context == 'network':
                try:
                    network = self.controller.get_or_create_network(self._generate_sidecar_name())

                    sidecar = self.controller.get_or_create_sidecar(
                        image='busybox',
                        command=self.command,
                        name=self._generate_sidecar_name(),
                        volumes='',
                        networks=''
                    )
                    self.target = self.sut.target
                except Exception as exc:
                    raise
            elif self.context == 'service':
                self.target = self.sut.service_id
