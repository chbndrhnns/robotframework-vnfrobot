import subprocess
from collections import namedtuple

import time
from docker import errors
import docker
from robot.api import logger

from testutils import Result

ProcessResult = namedtuple('ProcessResult', 'stdout stderr')


class DockerController():
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self._docker = docker.from_env()

    def get_env(self, container):
        try:
            c = self._docker.containers.get(container)
        except docker.errors.ContainerError as exc:
            logger.console("Cannot find container {}: {}".format(container, exc))
            return Result.FAIL

        return c.attrs['Config']['Env']

    def get_containers(self):
        return self._docker.containers.list()

    def run_sidecar(self, image=None, goss_config=None, command=None):
        try:
            self._docker.images.get(image)
        except docker.errors.ImageNotFound:
            self._docker.images.pull(image)

        try:
            result = self._docker.containers.run(image=image, command=command, auto_remove=True, network_mode='host', tty=True)
            logger.console(result)
        except docker.errors.ContainerError as exc:
            logger.console(exc)
            return Result.FAIL

        return Result.PASS

    def dispatch(self, options, project_options=None, returncode=0):
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
    print("Running process: %s" % proc.pid)
    return proc


def wait_on_process(proc, returncode=0):
    stdout, stderr = proc.communicate()
    if proc.returncode != returncode:
        print("Stderr: {}".format(stderr))
        print("Stdout: {}".format(stdout))
        assert proc.returncode == returncode
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