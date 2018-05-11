# helpers from https://github.com/docker/compose/blob/master/tests/acceptance/cli_test.py
import subprocess
import time
from string import lower

import docker
from docker.models.containers import Container
from docker.models.services import Service
from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn

from exc import DeploymentError
from settings import Settings
from tools.data_structures import ProcessResult


def start_process(base_dir, options):
    proc = subprocess.Popen(
        ['docker'] + options,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=base_dir)
    BuiltIn().log("Running process: %s" % proc.pid,
                  level='INFO',
                  console=Settings.to_console)
    return proc


def wait_on_process(proc, returncode=0):
    stdout, stderr = proc.communicate()
    if proc.returncode != returncode:
        BuiltIn().log("Stderr: {}".format(stderr),
                      level='INFO',
                      console=Settings.to_console)
        BuiltIn().log("Stdout: {}".format(stdout),
                      level='INFO',
                      console=Settings.to_console)
        # assert proc.returncode == returncode
    return ProcessResult(stdout.decode('utf-8'), stderr.decode('utf-8'))


def wait_on_condition(condition, delay=0.1, timeout=40):
    start_time = time.time()
    # last_time = start_time
    while not condition():
        if time.time() - start_time > timeout:
            raise AssertionError("Timeout: %s" % condition)
        # if time.time() - last_time > 15:
        #     BuiltIn().log('Waiting since {} seconds now...'.format(time.time() - start_time),
        # level='DEBUG', console=Settings.to_console)
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


# noinspection PyProtectedMember
def wait_on_container_status(client, container, status='Running'):
    """
    Wait until a container is in the desired state.

    Args:
        client: DockerController
        container: container name to search for
        status: str,list desired status, can also be a list of states, default: Running

    Returns:

    """

    def condition():
        # noinspection PyProtectedMember
        res = container if isinstance(container, Container) else client._docker.containers.get(container)
        if res and isinstance(status, basestring):
            if 'Running' in status:
                return res.attrs['State'][status]
            if 'Created' in status:
                return res.attrs['State']['Status'] == 'created'
        if res and isinstance(status, list) and len(status) > 0:
            found = False
            for s in status:
                if 'Running' in s:
                    found = res.attrs['State'][status]
                elif 'Created' in s:
                    found = res.attrs['State']['Status'] == 'created'
                elif 'Exited' in s:
                    found = res.attrs['State']['Status'] == 'exited'
                if found:
                    return found
        return False

    container = container.name if isinstance(container, Container) else container
    # logger.console('Waiting for {} to be {}...'.format(container, status))
    assert isinstance(client._docker, docker.DockerClient)
    return wait_on_condition(condition)


# noinspection PyProtectedMember
def wait_on_service_status(client, service, status='Running'):
    """
    Wait until a service is in the desired state.

    Args:
        client: DockerController
        service: service name to search for
        status: desired status, default: Running

    Returns:

    """

    # noinspection PyProtectedMember
    def condition():
        res = service if isinstance(service, Service) else client._docker.services.get(service)
        if res:
            return res.attrs['State'][status] is True
        return False

    assert isinstance(client._docker, docker.DockerClient)
    return wait_on_condition(condition)


# noinspection PyProtectedMember
def wait_on_service_container_status(client, service=None, current_instances=None, status='running'):
    """
    Wait until a first container that belongs to a service is in the desired state.
    If current_instances is given, the wait routine on returns when there is a disjoint set of old and new instances.

    Args:
        current_instances: list of containers
        client: DockerController
        service: service name to search for
        status: desired status, default: Running

    Returns:

    """

    def condition():
        # logger.console('waiting for {} to have a container in state {}'.format(service, status))
        # noinspection PyProtectedMember
        res = client._docker.containers.list(filters={
            'label': 'com.docker.swarm.service.name={}'.format(service),
            'status': lower(status)
        })
        # logger.console([c.name for c in res])

        if not current_instances:
            return True if res else False
        else:
            if not res:
                return False
            new_instances = frozenset(res)
            # logger.console('current_instances {}, new_instances: {}'.format(current_instances, new_instances))
            return new_instances.isdisjoint(current_instances)

    service = service.name if isinstance(service, Service) else service
    assert isinstance(client._docker, docker.DockerClient)
    assert isinstance(service, basestring)
    return wait_on_condition(condition)


# noinspection PyProtectedMember
def wait_on_services_status(client, services=None):
    """
    Wait until all provided services are in the desired state.

    Args:
        services: List of services to wait for
        client: DockerController

    Returns:

    """

    # noinspection PyProtectedMember,PyProtectedMember,PyProtectedMember
    def condition():
        if isinstance(services, list) and len(services) > 0:
            state_ok = 0
            for service in services:
                service_name = service.name if isinstance(service, Service) else service

                res = client._docker.containers.list(filters={
                    'label': 'com.docker.swarm.service.name={}'.format(service_name)
                })

                if res:
                    # logger.console('Found container {} belonging to service {}...'.format(res[0].name, service))
                    state_ok += 1
                else:
                    # BuiltIn().log('Waiting for service {}...'.format(service_name),
                    #               level='DEBUG',
                    #               console=Settings.to_console)

                    # try to find out if an error occured
                    tasks = service.tasks(filters={"desired-state": "Ready"})
                    if len(tasks) > 0:
                        task = tasks[0]
                        err = task.get('Status', {}).get('Err')
                        if err:
                            if 'failed to allocate gateway' in err:
                                client._docker_api.prune_networks()
                            elif 'No such image' in err:
                                raise DeploymentError('Service {}: {}'.format(service_name, err))
                            else:
                                raise DeploymentError('Could not deploy {}: {}'.format(service.name, err))
            return len(services) == state_ok
        return False

    assert isinstance(client._docker, docker.DockerClient)
    return wait_on_condition(condition)
