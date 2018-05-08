from exc import ValidationError
from testtools.TestTool import TestTool
from tools.matchers import string_matchers, all_matchers
from tools.testutils import get_truth, timeit


class DockerTool(TestTool):

    def __init__(self, controller=None, sut=None):
        super(DockerTool, self).__init__(controller, sut)

    def run(self, target):
        self.target = target
        if not self.command:
            raise ValidationError('DockerTool: run(): No command given.')
        o = getattr(self, self.command, None)
        if callable(o):
            o()
        else:
            raise ValidationError('DockerTool: run(): Cannot find command "{}" in DockerTool.'.format(self.command))

    def env_vars(self):
        self.test_results = self.controller.get_container_config(self.sut.service_id, 'Env')

    def get_container_labels(self):
        self.test_results = self.controller.get_container_config(self.sut.service_id, 'Labels')

    def run_in_container(self):
        self.test_results = self.controller.execute(self.sut.service_id, self.target.entity)

    @timeit
    def placement(self):
        labels = self.controller.get_container_config(self.sut.service_id, 'Labels')
        node_id = labels.get('com.docker.swarm.node.id')
        node = self.controller.get_node(node_id)
        self.test_results = node.attrs

    def process_results(self, target):
        if not self.command:
            raise ValidationError('DockerTool: No command given.')
        if not self.test_results:
            raise ValidationError('DockerTool: No {} "{}" found.'.format(self.command, target.entity))

        method_name = '_process_{}'.format(self.command)
        m = getattr(self, method_name, None)
        if not m:
            raise ValidationError('There is no method {} in DockerTool.'.format(method_name))
        res = m(entity=target.entity)

        actual = res[0] if isinstance(res, list) else res

        if not get_truth(actual, all_matchers[target.matcher], target.value):
            raise ValidationError(
                '{}: {} {} {}, actual: {}'.format(
                    target.entity,
                    target.property if target.property else target.entity,
                    target.matcher,
                    target.value,
                    actual)
            )

    def _process_env_vars(self, entity):
        return [e.split('=')[1] for e in self.test_results if entity == e.split('=')[0]]

    def _process_placement(self, entity):
        # role is in obj.attrs['Spec']['Role']
        # labels are  in obj.attrs['Spec']['Labels']

        return self.test_results.get('Spec', {}).get('Role', '')

    def _process_run_in_container(self, entity):
        if 'return code' in self.target.property:
            return self.test_results.get('code', '')
        else:
            return self.test_results.get('res', '').strip()

