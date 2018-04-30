from exc import ValidationError
from testtools.TestTool import TestTool
from tools.matchers import string_matchers
from tools.testutils import get_truth


class DockerTool(TestTool):

    def __init__(self, controller=None, sut=None):
        super(DockerTool, self).__init__(controller, sut)

    def run(self):
        if not self.command:
            raise ValidationError('DockerTool: No command given.')
        o = getattr(self, self.command, None)
        o()

    def env_vars(self):
        self.test_results = self.controller.get_container_config(self.sut.service_id, 'Env')

    def get_container_labels(self):
        self.test_results = self.controller.get_container_config(self.sut.service_id, 'Labels')

    def get_node_labels(self):
        labels = self.controller.get_container_config(self.sut.service_id, 'Labels')
        node_id = labels.get('com.docker.swarm.node.id')
        node = self.controller.get_node(node_id)
        self.test_results = node.labels

    def process_results(self, target):
        if not self.test_results:
            raise ValidationError('No variable "{}" found.'.format(target.entity))

        res = getattr(self, '_process_{}'.format(self.command))(entity=target.entity)

        if not get_truth(res[0], string_matchers[target.matcher], target.value):
            raise ValidationError(
                'Variable {}: {} {}, actual: {}'.format(
                    target.entity,
                    target.matcher,
                    target.value,
                    res[0])
            )

    def _process_env_vars(self, entity):
        return [e.split('=')[1] for e in self.test_results if entity == e.split('=')[0]]