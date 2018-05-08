import json
import tempfile

from robot.libraries.BuiltIn import BuiltIn

import exc
from exc import DeploymentError, TestToolError, NotFoundError
from testtools.TestTool import TestTool
from tools.testutils import timeit


class GossTool(TestTool):
    # TODO remove context from signature
    def __init__(self, controller=None, sut=None, gossfile='/goss.yaml'):
        TestTool.__init__(self, controller, sut)

        self.gossfile = gossfile
        self.command = '/goss/goss-linux-amd64 --gossfile {} validate --format json'.format(self.gossfile)

    def run(self, target):
        res = ''
        try:
            if not self.sut:
                raise AttributeError('Target is necessary to run goss.')
            if not self.controller:
                raise AttributeError('Controller is necessary to run goss.')

            res = self.controller.execute(self.sut.target, self.command)
            self.test_results = json.loads(res.get('res', {}).strip())
            return self.test_results
        except NotFoundError as exc:
            raise exc
        except (json.JSONDecoder, ValueError) as exc:
            res = res.get('res', {}).strip()
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
            raise DeploymentError('Could not run command in {}: {}'.format(self.sut.target, exc))

    def process_results(self, target):
        if not self.test_results:
            raise exc.ValidationError('No variable "{}" found.'.format(target.entity))

        assert isinstance(self.test_results['summary']['failed-count'], int)

        BuiltIn().log_to_console(json.dumps(self.test_results, indent=4, sort_keys=True))

        errors = [res for res in self.test_results['results'] if not res['successful']]
        if errors:
            for err in errors:
                BuiltIn().log('Port {}: property {}, expected: {}, actual: {}'.format(
                    target.entity,
                    err.get('property', ''),
                    err.get('expected'),
                    err.get('found')), level='INFO', console=True)
            raise exc.ValidationError('Test not successful')

    @staticmethod
    def inject_gossfile(target):
        with tempfile.NamedTemporaryFile() as f:
            try:
                f.write(target.transformed_data)
                f.seek(0)

                target.instance.docker_controller.put_file(
                    entity=target.instance.sut.target,
                    file_to_transfer=f.name,
                    filename='goss.yaml')
            except (TypeError, ValueError) as exc:
                raise exc.ValidationError('ValidationError: {}'.format(exc))
            except DeploymentError as exc:
                raise DeploymentError('Could not run test tool on {}: {}'.format(target.instance.sut, exc))

