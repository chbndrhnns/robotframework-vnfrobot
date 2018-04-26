# helpers from https://github.com/docker/compose/blob/master/tests/acceptance/cli_test.py
import subprocess
import time
from collections import namedtuple
from string import lower

import docker
from docker.models.containers import Container
from docker.models.services import Service
from robot.api import logger


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
        res = service if isinstance(service, Service) else client.services.get(service)
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
        res = container if isinstance(container, Container) else client.containers.get(container)
        if res:
            return res.attrs['State']['Status'] == 'created'
        return False

    container = container.name if isinstance(container, Container) else container
    # logger.console('Waiting for {}...'.format(container))
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
        res = container if isinstance(container, Container) else client.containers.get(container)
        if res:
            return res.attrs['State'][status] == True
        return False

    container = container.name if isinstance(container, Container) else container
    # logger.console('Waiting for {}...'.format(container))
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
        res = service if isinstance(service, Service) else client.services.get(service)
        if res:
            return res.attrs['State'][status] == True
        return False

    assert isinstance(client, docker.DockerClient)
    return wait_on_condition(condition)


def wait_on_service_container_status(client, service=None, current_instances=None, status='running'):
    """
    Wait until a first container that belongs to a service is in the desired state.
    If current_instances is given, the wait routine on returns when there is a disjoint set of old and new instances.

    Args:
        current_instances: list of containers
        client: Docker client
        service: service name to search for
        status: desired status, default: Running

    Returns:

    """

    def condition():
        # logger.console('waiting for {} to have a container in state {}'.format(service, status))
        res = client.containers.list(filters={
            'label': 'com.docker.swarm.service.name={}'.format(service),
            'status': lower(status)
        })

        if not current_instances:
            return True if res else False
        else:
            new_instances = frozenset(res)
            # logger.console('current_instances {}'.format(current_instances))
            # logger.console('new_instances {}'.format(new_instances))
            return new_instances.isdisjoint(current_instances)

    service = service.name if isinstance(service, Service) else service
    assert isinstance(client, docker.DockerClient)
    assert isinstance(service, basestring)
    return wait_on_condition(condition)


def wait_on_services_status(client, services=None, status='Running'):
    """
    Wait until all provided services are in the desired state.

    Args:
        services: List of services to wait for
        client: Docker client
        status: desired status, default: Running

    Returns:

    """

    def condition():
        if isinstance(services, list) and len(services) > 0:
            state_ok = 0
            for service in services:
                if isinstance(service, Service):
                    res = client.containers.list(filters={'label': 'com.docker.swarm.service.name={}'.format(service.name)})
                else:
                    res = client.containers.list(filters={'label': 'com.docker.swarm.service.name={}'.format(service)})
                if res:
                    # logger.console('Found container {} belonging to service {}...'.format(res[0].name, service))
                    state_ok += 1
            return len(services) == state_ok
        return False

    assert isinstance(client, docker.DockerClient)
    return wait_on_condition(condition)


ProcessResult = namedtuple('ProcessResult', 'stdout stderr')