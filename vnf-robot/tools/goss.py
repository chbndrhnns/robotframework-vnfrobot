from exc import DeploymentError, TestToolError


class GossTool:

    def __init__(self, controller, target):
        self.gossfile = '/goss.yaml'
        self.command = '/goss/goss-linux-amd64 validate {}'.format(self.gossfile)
        self.controller = controller
        self.target = target

    def run_goss(self):
        try:
            res = self.controller.execute(self.target, self.command).strip()
            if 'No help topic' in res:
                raise TestToolError('Syntax error while calling goss on {}: {}'.format(self.target.name, res))
            if 'File error: open' in res:
                raise TestToolError('Gossfile not found on {}: {}'.format(self.target.name, self.gossfile))
            if 'no such file or directory' or 'executable file not found in' in res:
                raise TestToolError('goss executable was not found on {}: {}'.format(self.target.name, res))
            return res
        except DeploymentError as exc:
            raise

