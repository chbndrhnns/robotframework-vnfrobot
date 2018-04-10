import subprocess
from collections import namedtuple

import time
from string import lower

from docker import errors
import docker
from robot.api import logger

import exc
from testutils import Result

ProcessResult = namedtuple('ProcessResult', 'stdout stderr')


class DockerController():
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self._docker = docker.from_env()
        self.helper = 'helper'

    def get_env(self, entity):

        # first, try if entity is a container
        try:
            wait_on_container_status(self._docker, entity)
            c = self._docker.containers.get(entity)
        except docker.errors.NotFound as exc:
            logger.console('{} is not a container. Trying as service...'.format(entity))

            # second, try if entity is a service
            try:
                wait_on_service_replication(self._docker, entity)
                self._docker.services.get(entity)
                wait_on_service_container_status(self._docker, entity)
                c = self._docker.containers.list(all=True,
                                                 filters={'label': 'com.docker.swarm.service.name={}'.format(entity)})
            except docker.errors.ContainerError as exc:
                logger.console("Cannot find container or service {}: {}".format(entity, exc))
                return Result.FAIL

            if isinstance(c, list):
                logger.debug("Found {} containers in this service. Getting env for one should be enough.".format(len(c)))
                return c[0].attrs['Config']['Env']

        return c.attrs['Config']['Env']

    def get_service(self, service):
        try:
            s = self._docker.services.get(service)
        except docker.errors.NotFound as exc:
            logger.console("Cannot find service {}: {}".format(service, exc))
            return Result.FAIL

        return s

    def get_container(self, container):
        return self._docker.containers.get(container)

    def remove_container(self, container):
        c = self._docker.containers.get(container)
        c.stop()
        c.remove()

    def get_containers(self):
        return self._docker.containers.list()

    def stack_deploy(self, descriptor, name):
        return self._dispatch(['stack', 'deploy', '-c', descriptor, name])

    def stack_undeploy(self, name):
        return self._dispatch(['stack', 'rm', name])

    def create_volume(self, name):
        return self._dispatch(['volume', 'create', name])

    def get_volume(self, name):
        res = self._dispatch(['volume', 'inspect', name])
        if res.stderr:
            return exc.SetupError('Could not find volume {}'.format(name))

    def add_data_to_volume(self, volume, path):
        try:
            self.remove_container(self.helper)
        except docker.errors.NotFound:
            pass

        res = self._dispatch(['run', '-v', '{}:/data'.format(volume), '--name', self.helper, 'busybox', 'true'])
        assert len(res.stderr) == 0
        res = self._dispatch(['cp', '{}/.'.format(path), '{}:/data'.format(self.helper)])
        assert len(res.stderr) == 0
        res = self._dispatch(['stop', self.helper])
        assert len(res.stderr) == 0
        res = self._dispatch(['rm', self.helper])
        assert len(res.stderr) == 0

    def list_files_on_volume(self, volume):
        try:
            self.get_volume(volume)
        except exc.SetupError:
            raise

        res = self._dispatch(['run', '--rm', '-v', '{}:/data'.format(volume), 'busybox', 'ls', '/data'])
        assert len(res.stderr) == 0

        return res

    def run_sidecar(self, image=None, goss_config=None, command=None):
        try:
            self._docker.images.get(image)
        except docker.errors.ImageNotFound:
            self._docker.images.pull(image)

        try:
            result = self._docker.containers.run(image=image, command=command, auto_remove=True, network_mode='host',
                                                 tty=True)
            logger.console(result)
        except docker.errors.ContainerError as exc:
            logger.console(exc)
            return Result.FAIL

        return Result.PASS

    def _dispatch(self, options, project_options=None, returncode=0):
        project_options = project_options or []
        o = project_options + options
        logger.console('Dispatching: docker {}'.format(o))
        proc = start_process(self.base_dir, o)
        return wait_on_process(proc, returncode=returncode)


### helpers from https://github.com/docker/compose/blob/master/tests/acceptance/cli_test.py

def start_process(base_dir, options):
    proc = subprocess.Popen(
        ['docker'] + options,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=base_dir)
    logger.console("Running process: %s" % proc.pid)
    return proc


def wait_on_process(proc, returncode=0):
    stdout, stderr = proc.communicate()
    if proc.returncode != returncode:
        logger.console("Stderr: {}".format(stderr))
        logger.console("Stdout: {}".format(stdout))
        # assert proc.returncode == returncode
    return ProcessResult(stdout.decode('utf-8'), stderr.decode('utf-8'))


def wait_on_condition(condition, delay=0.1, timeout=40):
    start_time = time.time()
    while not condition():
        if time.time() - start_time > timeout:
            raise AssertionError("Timeout: %s" % condition)
        time.sleep(delay)


def kill_service(service):
    for container in service.containers():
        if container.is_running:
            container.kill()


def wait_on_service_replication(client, service):
    def condition():
        res = client.services.get(service)
        replicas = res.attrs['Spec']['Mode']['Replicated']['Replicas']
        return replicas > 0

    # logger.console('Waiting for service {}...'.format(service))
    return wait_on_condition(condition)


def wait_on_container_status(client, container, status='Running'):
    """
    Wait until a container is in the desired state.

    Args:
        client: Docker client
        service: service name to search for
        status: desired status, default: Running

    Returns:

    """

    def condition():
        res = client.containers.get(container)
        if res:
            return res.attrs['State'][status] == True
        return False

    return wait_on_condition(condition)


def wait_on_service_container_status(client, service=None, status='Running'):
    """
    Wait until a first container that belongs to a service is in the desired state.

    Args:
        client: Docker client
        service: service name to search for
        status: desired status, default: Running

    Returns:

    """

    def condition():
        if service:
            res = client.containers.list(filters={'label': 'com.docker.swarm.service.name={}'.format(service)})
        if res:
            return lower(res[0].attrs['State']['Status']) == lower(status)
        return False

    # logger.console('Waiting for a container belonging to service {}...'.format(service))
    return wait_on_condition(condition)
