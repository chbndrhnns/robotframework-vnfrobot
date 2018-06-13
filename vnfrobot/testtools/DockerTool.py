from exc import ValidationError
from settings import set_breakpoint
from testtools.TestTool import TestTool
from tools.matchers import all_matchers
from tools.testutils import get_truth


class DockerTool(TestTool):

    def __init__(self, controller=None, sut=None):
        super(DockerTool, self).__init__(controller, sut)

    def run(self, target):
        self.target = target
        if not self.command:
            raise ValidationError('DockerTool: run(): No command given.')
        command = getattr(self, self.command, None)
        if callable(command):
            command()
        else:
            raise ValidationError('DockerTool: run(): Cannot find command "{}" in DockerTool.'.format(self.command))

    def env_vars(self):
        """
        Retrieve environment variables for a container or service

        Returns:
            list

        """
        self.test_results = self.controller.get_container_config(self.sut.service_id, 'Env')

    def get_container_labels(self):
        """
        Retrieve labels for a container

        Returns:
            list

        """
        self.test_results = self.controller.get_container_config(self.sut.service_id, 'Labels')

    def logs(self):
        """
        Retrieve standard error and standard output logs for a container

        Returns:
            dict

        """
        container = self.controller.get_containers_for_service(self.sut.service_id)
        assert len(container) > 0, "DockerTool: logs(): we need at least one container to continue here."
        self.test_results = self.controller.get_container_logs(container[0])

    def run_in_container(self):
        """
        Run a command inside a container (aka docker exec)

        Returns:
            dict

        """
        if 'service' in self.sut.target_type:
            target = self.controller.get_containers_for_service(self.sut.service_id)[0]
        else:
            target = self.sut.target
        self.test_results = self.controller.execute(target, self.target.entity)

    def placement(self):
        """
        Retrieve placement information for a container

        Returns:

        """
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

        set_breakpoint()

        if not get_truth(actual, all_matchers[target.matcher], target.value):
            raise ValidationError(
                'Expected: {} {} {} "{}", \nActual: {}'.format(
                    '"{}":'.format(target.entity) if target.entity else '',
                    target.property if target.property else target.entity,
                    target.matcher,
                    target.value if target.value else '',
                    actual)
            )

    def _process_env_vars(self, entity):
        return [e.split('=')[1] for e in self.test_results if entity == e.split('=')[0]]

    def _process_logs(self, entity):
        return self.test_results.get('res')

    def _process_placement(self, entity):
        # role is in obj.attrs['Spec']['Role']
        # labels are  in obj.attrs['Spec']['Labels']

        return self.test_results.get('Spec', {}).get('Role', '')

    def _process_run_in_container(self, entity):
        if 'return code' in self.target.property:
            return self.test_results.get('code', '')
        else:
            assert isinstance(self.test_results, dict), '_process_run_in_container: dict expected for res'
            return self.test_results.get('res', '').strip()

