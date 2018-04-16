import json

from exc import DeploymentError, TestToolError


class GossTool:
    def __init__(self, controller, target, gossfile='/goss.yaml'):
        self.gossfile = gossfile
        self.command = '/goss/goss-linux-amd64 --gossfile /{} validate --format json'.format(self.gossfile)
        self.controller = controller
        self.target = target

    def run(self):
        res = ''
        try:
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
        except DeploymentError as exc:
            raise

