import subprocess
from collections import namedtuple

import time
from string import lower

import os
from docker import errors
import docker
from docker.models.containers import Container
from docker.models.networks import Network
from docker.models.services import Service
from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn

from tools import namesgenerator
from tools.archive import Archive

from exc import NotFoundError, SetupError, DeploymentError
from tools.testutils import Result

ProcessResult = namedtuple('ProcessResult', 'stdout stderr')


class DockerController:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self._docker = docker.from_env()
        self._docker_api = docker.APIClient(base_url='unix://var/run/docker.sock')
        self.helper = 'helper'

        if not self.base_dir:
            self.base_dir = os.getcwd()
            BuiltIn().log('base_dir not specified. Assuming current working dir: {}')

    def run_busybox(self):
        try:
            name = namesgenerator.get_random_name()
            self._docker.containers.run('busybox', 'true', name=name, detach=True)
            return self._docker.containers.get(name)
        except docker.errors.NotFound as exc:
            raise NotFoundError(exc)
        except docker.errors.APIError as exc:
            raise DeploymentError(exc)

    def execute(self, container=None, command=None):
        if not command:
            raise ValueError('command parameter must not be empty.')

        wait_on_container_status(self._docker, container.id, 'Running')

        try:
            res = container.exec_run(cmd=command, tty=True)
            return res
        except docker.errors.APIError as exc:
            raise SetupError(exc)

    def get_containers_for_service(self, service):
        try:
            wait_on_service_replication(self._docker, service)
            # self._docker.services.get(service)
            wait_on_service_container_status(self._docker, service)
            return self._docker.containers.list(all=True,
                                                filters={'label': 'com.docker.swarm.service.name={}'.format(service)})
        except docker.errors.NotFound as exc:
            raise NotFoundError(exc)

    def get_env(self, entity):
        # first, try if entity is a container
        try:
            wait_on_container_status(self._docker, entity)
            c = self._docker.containers.get(entity)
        except docker.errors.NotFound as exc:
            # second, try if entity is a service

            try:
                c = self.get_containers_for_service(entity)
            except NotFoundError as exc:
                raise NotFoundError('Could not find service {}'.format(entity))

            if isinstance(c, list):
                # BuiltIn().log(
                #     "Found {} containers in this service. Getting env for one should be enough.".format(len(c)),
                #     level='DEBUG', console=True)
                return c[0].attrs['Config']['Env']

        return c.attrs['Config']['Env']

    def get_service(self, service):
        try:
            wait_on_service_replication(self._docker, service)
            s = self._docker.services.get(service)
        except docker.errors.NotFound as exc:
            raise NotFoundError('Cannot find service {}: {}'.format(service, exc))

        return s

    def get_container(self, container):
        return self._docker.containers.get(container)

    def get_containers(self):
        return self._docker.containers.list()

    def connect_service_to_network(self, service, network):
        try:
            wait_on_service_replication(self._docker, service)
            wait_on_service_container_status(self._docker, service)

            n = network if isinstance(network, Network) else self.get_network(network)
            s = service if isinstance(service, Service) else self.get_service(service)
        except (docker.errors.NotFound, docker.errors.APIError, NotFoundError) as exc:
            raise DeploymentError('Entity not found: {}'.format(exc))

        try:
            s.update(networks=[n.name])

            # wait for the update to take place
            wait_on_service_replication(self._docker, service)
            wait_on_service_container_status(self._docker, service)
            c = self.get_containers_for_service(service)[0]
            wait_on_container_status(self._docker, c)
            return s
        except docker.errors.APIError as exc:
            raise DeploymentError('Could not connect network to container: {}'.format(exc))

    def deploy_stack(self, descriptor, name):
        res = self._dispatch(['stack', 'deploy', '-c', descriptor, name])
        if res.stderr:
            raise DeploymentError(res.stderr)
        return True

    def undeploy_stack(self, name):
        return self._dispatch(['stack', 'rm', name])

    def get_network(self, name):
        try:
            return self._docker.networks.get(name)
        except docker.errors.NotFound:
            raise

    def create_network(self, name, driver='overlay'):
        try:
            return self._docker.networks.create(
                name=name,
                driver=driver,
                scope='swarm' if driver == 'overlay' else 'local',
                attachable=True)
        except docker.errors.APIError as exc:
            if 'already exists' in exc:
                return self._docker.networks.get(name)
            else:
                raise
        # self._dispatch(['network', 'create', name, '--attachable', '--scope', 'swarm'])
        # return self.get_network(name)

    def delete_network(self, name):
        n = self._docker.networks.get(name)
        if n.containers:
            for c in n.containers:
                n.disconnect(c)

        n.remove()

    def create_volume(self, name):
        return self._dispatch(['volume', 'create', name])

    def delete_volume(self, name):
        return self._dispatch(['volume', 'rm', name])

    def get_volume(self, name):
        res = self._dispatch(['volume', 'inspect', name])
        if res.stderr:
            return SetupError('Could not find volume {}'.format(name))

    def add_data_to_volume(self, volume, path):
        try:
            self._kill_and_delete_container(self.helper)
        except docker.errors.NotFound:
            pass

        try:
            res = self._dispatch(['run', '-v', '{}:/data'.format(volume), '--name', self.helper, 'busybox', 'true'])
            assert len(res.stderr) == 0
            res = self._dispatch(['cp', '{}/.'.format(path), '{}:/data'.format(self.helper)])
            assert len(res.stderr) == 0
        finally:
            res = self._dispatch(['stop', self.helper])
            assert len(res.stderr) == 0
            res = self._dispatch(['rm', self.helper])
            assert len(res.stderr) == 0

    def list_files_on_volume(self, volume):
        try:
            self.get_volume(volume)
        except SetupError as exc:
            raise exc

        res = self._dispatch(['run', '--rm', '-v', '{}:/data'.format(volume), 'busybox', 'ls', '/data'])
        assert len(res.stderr) == 0

        return res

    def create_or_get_sidecar(self, image, command, name, volumes=None, network=None):
        # retrieve image
        try:
            self._docker.images.get(image)
        except docker.errors.ImageNotFound:
            try:
                self._docker.images.pull(image)
            except docker.errors.ImageNotFound:
                raise DeploymentError('Image {} not found.'.format(image))

        try:
            c = self._docker.containers.get(name)
            if isinstance(c, Container):
                logger.console('Found container {}. Re-using it as sidecar.'.format(name))
                return c
        except docker.errors.NotFound:
            pass

        try:
            logger.console('Found container {}. Re-using it as sidecar.'.format(name))
            return self._docker.containers.create(name=name if name else None,
                                                  image=image,
                                                  command=command,
                                                  auto_remove=False,
                                                  volumes=volumes,
                                                  network=network,
                                                  tty=True)
        except docker.errors.APIError as exc:
            raise DeploymentError('Could not deploy sidecar: {}'.format(exc))
        except docker.errors.ImageNotFound as exc:
            raise DeploymentError('Invalid image name: {}'.format(exc))
        except docker.errors.ContainerError as exc:
            BuiltIn().log(exc, level='DEBUG', console=True)
            raise DeploymentError('Error: {}'.format(exc))

    def run_sidecar(self, name='', sidecar=None, image='busybox', command='true', volumes=None, network=None):
        stdout, stderr = '', ''
        try:
            if not sidecar:
                sidecar = self.create_or_get_sidecar(image, command, name, volumes, network)
            wait_on_container_created(self._docker, sidecar)
            sidecar.start()
            sidecar.wait()
            stdout = sidecar.logs(stdout=True, stderr=False)
            stderr = sidecar.logs(stdout=False, stderr=True)

            BuiltIn().log(stdout, level='DEBUG', console=True)

            if stderr:
                raise DeploymentError('Found stderr: {}'.format(stderr))
        except docker.errors.APIError as exc:
            if 'executable file not found' in exc.explanation:
                raise DeploymentError('Could not run command: {}'.format(exc))
            else:
                raise DeploymentError('Could not deploy sidecar: {}'.format(exc))
        except docker.errors.ImageNotFound as exc:
            raise DeploymentError('Invalid image name: {}'.format(exc))
        except docker.errors.ContainerError as exc:
            BuiltIn().log(exc, level='DEBUG', console=True)
            raise DeploymentError('Error: {}'.format(exc))
        finally:
            self._kill_and_delete_container(sidecar)

        return ProcessResult(stdout, stderr)

    def _dispatch(self, options, project_options=None, returncode=0):
        project_options = project_options or []
        o = project_options + options
        BuiltIn().log('Dispatching: docker {}'.format(o), level='DEBUG')
        proc = start_process(self.base_dir, o)
        return wait_on_process(proc, returncode=returncode)

    def find_stack(self, deployment_name):
        res = self._dispatch(['stack', 'ps', deployment_name, '--format', '" {{ .Name }}"'])

        if deployment_name in res.stdout.strip('\n\r'):
            return True
        return False

    def put_file(self, entity, file_to_transfer='', destination='/', filename=None):
        if not os.path.isfile(file_to_transfer):
            raise NotFoundError('File {} not found'.format(file_to_transfer))

        if isinstance(entity, Container):
            entity = entity.name

        filename = filename or os.path.basename(file_to_transfer)
        with open(file_to_transfer, 'r') as f:
            content = f.read()
            self._send_file(content, destination, entity, filename)

    def _send_file(self, content, destination, entity, filename):
        to_send = Archive('w').add_text_file(filename, content).close()
        try:
            BuiltIn().log('Putting file {} on {} at {}'.format(filename, entity, destination), level='DEBUG')
            res = self._docker_api.put_archive(entity, destination, to_send.buffer)
            assert res
            # self.file_exists(entity, filename)
        except docker.errors.APIError as exc:
            raise DeploymentError(exc)

    def get_file(self, entity, path, filename):
        try:
            strm, stat = self._docker_api.get_archive(entity, '{}/{}'.format(path, filename))
        except docker.errors.APIError as exc:
            raise DeploymentError(exc)

        return Archive('r', strm.read()).get_text_file(filename)

    def _kill_and_delete_container(self, name):
        try:
            c = self._docker.containers.get(name) if isinstance(name, basestring) else name
            if hasattr(c, 'status') and lower(c.status) == 'running':
                c.kill()
                c.remove()
        except docker.errors.APIError as exc:
            if 'No such container' in exc.explanation:
                pass
            elif 'is not running' in exc.explanation:
                pass
            else:
                raise


# helpers from https://github.com/docker/compose/blob/master/tests/acceptance/cli_test.py

def start_process(base_dir, options):
    proc = subprocess.Popen(
        ['docker'] + options,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=base_dir)
    logger.debug("Running process: %s" % proc.pid)
    return proc


def wait_on_process(proc, returncode=0):
    stdout, stderr = proc.communicate()
    if proc.returncode != returncode:
        logger.debug("Stderr: {}".format(stderr))
        logger.debug("Stdout: {}".format(stdout))
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


def wait_on_container_created(client, container):
    """
    Wait until a container is in the created state.

    Args:
        client: Docker client
        container: container name to search for

    Returns:

    """

    def condition():
        res = client.containers.get(container)
        if res:
            return res.attrs['State']['Status'] == 'created'
        return False

    container = container.name if isinstance(container, Container) else container
    logger.console('Waiting for {}...'.format(container))
    assert isinstance(client, docker.DockerClient)
    return wait_on_condition(condition)


def wait_on_container_status(client, container, status='Running'):
    """
    Wait until a container is in the desired state.

    Args:
        client: Docker client
        container: container name to search for
        status: desired status, default: Running

    Returns:

    """

    def condition():
        res = client.containers.get(container)
        if res:
            return res.attrs['State'][status] == True
        return False

    container = container.name if isinstance(container, Container) else container
    logger.console('Waiting for {}...'.format(container))
    assert isinstance(client, docker.DockerClient)
    return wait_on_condition(condition)


def wait_on_service_status(client, service, status='Running'):
    """
    Wait until a service is in the desired state.

    Args:
        client: Docker client
        service: service name to search for
        status: desired status, default: Running

    Returns:

    """

    def condition():
        res = client.services.get(service)
        if res:
            return res.attrs['State'][status] == True
        return False

    assert isinstance(client, docker.DockerClient)
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
                # logger.console('Found container {} belonging to service {}...'.format(res[0].name, service))
                return lower(res[0].attrs['State']['Status']) == lower(status)
        # logger.console('Found no container belonging to service {}...'.format(service))
        return False

    assert isinstance(client, docker.DockerClient)
    return wait_on_condition(condition)
