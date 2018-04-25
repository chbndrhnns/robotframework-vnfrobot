import json
from abc import ABCMeta, abstractmethod

from exc import DeploymentError, TestToolError


class TestTool:
    __metaclass__ = ABCMeta

    def __init__(self):
        self.command = None
        self.controller = None
        self.target = None

    @abstractmethod
    def run(self):
        pass


class GossTool(TestTool):
    def __init__(self, controller=None, target=None, gossfile='/goss.yaml'):
        TestTool.__init__(self)

        self.gossfile = gossfile
        self.command = '/goss/goss-linux-amd64 --gossfile /{} validate --format json'.format(self.gossfile)
        self.controller = controller
        self.target = target
        self.sidecar = None

    def run(self):
        res = ''
        try:
            if not self.target:
                raise AttributeError('Target is necessary to run goss.')
            if not self.controller:
                raise AttributeError('Controller is necessary to run goss.')
            res = self.controller.execute(self.target, self.command).strip()
            return json.loads(res)
        except (json.JSONDecoder, ValueError) as exc:
            if 'No help topic' in res:
                raise TestToolError('Syntax error while calling goss on {}: {}'.format(self.target.name, res))
            elif 'File error: open' in res:
                raise TestToolError('Gossfile not found on {}: {}'.format(self.target.name, self.gossfile))
            elif 'Error: yaml:' in res or 'invalid character' in res:
                raise TestToolError('Syntax errors in provided yaml file {}: {}'.format(self.gossfile, res))
            elif 'no such file or directory' in res or 'executable file not found in' in res:
                raise TestToolError('goss executable was not found on {}: {}'.format(self.target.name, res))

            raise TestToolError('Could not parse return value from goss: {}'.format(res))
        except AttributeError as exc:
            raise TestToolError('Error: {}'.format(exc))
        except DeploymentError as exc:
            raise
