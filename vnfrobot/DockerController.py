import os
from string import lower

import docker
from docker import errors
from docker.models.containers import Container
from docker.models.networks import Network
from docker.models.services import Service
from docker.models.volumes import Volume
from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn

from InfrastructureController import InfrastructureController
from exc import NotFoundError, SetupError, DeploymentError
from settings import Settings
from tools import namesgenerator
from tools.archive import Archive
from tools.wait_on import wait_on_container_status, wait_on_service_replication, wait_on_service_container_status, \
    start_process, wait_on_process


class DockerController(InfrastructureController):
    """
    DockerController connects to a Docker instance and provides any functionality that is needed by the VnfValidator
    in terms of stacks, services, containers, networks and images
    """

    def __init__(self, base_dir):
        """
        The controller connects to the Docker host that is specified in the settings or to the socket on locallhost.

        Args:
            base_dir: str - is used to find docker-compose files.
        """
        super(DockerController, self).__init__()

        self.base_dir = base_dir
        self._docker = docker.from_env()
        self._docker_api = docker.APIClient(base_url=Settings.docker.get('DOCKER_HOST'))
        self.helper = 'helper'

        if not self.base_dir:
            self.base_dir = os.getcwd()
            BuiltIn().log('base_dir not specified. Assuming current working dir: {}'.format(self.base_dir), level='DEBUG',
                          console=Settings.to_console)

    def run_busybox(self, **kwargs):
        """
        Helper method for conftest.py to create a running dummy container.

        Args:
            **kwargs: any argument that a Container object takes except for image, command, name and detach

        Returns:
            Container

        """

        try:
            name = namesgenerator.get_random_name()
            command = kwargs.pop('command', 'sh -c "while true; do $(echo date "GET / HTTP/1.1"); sleep 1; done"')
            self._docker.containers.run('busybox', command=command, name=name, detach=True, **kwargs)
            return self._docker.containers.get(name)
        except docker.errors.NotFound as exc:
            raise NotFoundError(exc)
        except docker.errors.APIError as exc:
            raise DeploymentError(exc)

    def execute(self, entity=None, command=None):
        """
        Executes a command within a Docker container.

        Args:
            entity: Container object or container name or container id
            command: str or list - command to execute in the container

        Returns:
            dict: {
                'code': int,
                'rest': str
            }

        """
        target = entity if isinstance(entity, Container) else None

        if not target:
            try:
                target = self.get_container(entity)
            except (NotFoundError, TypeError):
                try:
                    target = self.get_containers_for_service(entity)[0]
                except (NotFoundError, TypeError):
                    raise NotFoundError(
                        'Could not find entity (service or container) {}'.format(entity if entity else '<None>'))

        BuiltIn().log('Running "{}" in {}'.format(command, target.name), level='INFO', console=Settings.to_console)
        container_status = target.status
        if 'created' in container_status:
            return self.run_sidecar(sidecar=target)
        else:
            return self._run_in_container(container=target, command=command)

    def _run_in_container(self, container=None, command=None):
        """
        Helper method for execute().

        Args:
            container:
            command:

        Returns:

        """
        if not command:
            raise ValueError('_command parameter must not be empty.')

        try:
            wait_on_container_status(self, container.name)

            # idea from https://github.com/docker/docker-py/issues/1989
            exec_id = container.client.api.exec_create(container.id, command)['Id']
            res = container.client.api.exec_start(exec_id)
            # res = container.exec_run(cmd=command)
            # res = container.exec_run(cmd=command, tty=True, stderr=True, stdout=True)
            ret_code = container.client.api.exec_inspect(exec_id)['ExitCode']
            return {
                'code': ret_code,
                'res': res
            }
        except (docker.errors.APIError, AttributeError) as exc:
            raise SetupError(exc)

    def get_containers_for_service(self, service, state='running'):
        """
        For the given service, wait until a timeout occurs or at least one container is in the specified state.

        Args:
            service: Service or service name or service id
            state: expected state of service

        Returns:
            [Container]

        """
        service = service.name if isinstance(service, Service) else service
        assert isinstance(service, basestring)

        try:
            wait_on_service_replication(self._docker, service)
            wait_on_service_container_status(self, service)
            res = self._docker.containers.list(all=True,
                                               filters={
                                                   'label': 'com.docker.swarm.service.name={}'.format(service),
                                                   'status': lower(state)
                                               })
            # BuiltIn().log('Get containers for services {}: {}'.format(
            #     service, [c.name for c in res ] if res else 'None'), level='DEBUG', console=Settings.to_console)
            if res:
                return res
            else:
                BuiltIn().log('No containers found for service {}'.format(service), level='INFO', console=True)
                raise NotFoundError
        except NotFoundError:
            raise
        except docker.errors.NotFound as exc:
            raise NotFoundError(exc)

    def get_container_config(self, entity, key=None):
        """
        Retrieve Config dictionary for a container. If key is specified, only return the key within the Config
        dictionary.

        Args:
            entity: Service or Container or service id or service name or container id or container name
            key: desired config key

        Returns:
            dict

        """
        if not entity:
            raise NotFoundError('No entity provided')

        # first, try if entity is a container
        try:
            wait_on_container_status(self, entity)
            c = self._docker.containers.get(entity)
        except docker.errors.NotFound:
            # second, try if entity is a service

            try:
                c = self.get_containers_for_service(entity)[0]
            except NotFoundError:
                raise NotFoundError('Could not find service {}'.format(entity))

        if key:
            return c.attrs['Config'].get(key, None)
        else:
            return c.attrs['Config']

    def get_node(self, node_id):
        """
        Retrieves a Node object for a given node ide

        Args:
            node_id: str

        Returns:
            docker.models.nodes.Node

        """
        return self._docker.nodes.get(node_id)

    def get_service(self, service):
        """
        Wait for service replication and retrieve a service.

        Args:
            service: Service or service id or service name

        Returns:
            docker.models.services.Service

        """
        try:
            wait_on_service_replication(self._docker, service)
            return self._docker.services.get(service)
        except docker.errors.NotFound as exc:
            raise NotFoundError('Cannot find service {}: {}'.format(service, exc))

    def get_container(self, container):
        """
        Retrieves a container by its name or id.

        Args:
            container: container name or container id

        Returns:
            docker.models.containers.Container

        """
        try:
            return self._docker.containers.get(container)
        except (docker.errors.NotFound, docker.errors.APIError) as exc:
            raise NotFoundError(exc)

    def get_containers(self, **kwargs):
        """
        Retrieve containers that match the filters specified by **kwargs. Refer to the Docker help for available
        filters.

        Args:
            **kwargs: filters

        Returns:
            [Container]

        """
        try:
            return self._docker.containers.list(**kwargs)
        except docker.errors.APIError as exc:
            raise NotFoundError('get_containers failed: {}'.format(exc))

    def get_container_logs(self, container):
        try:
            if not isinstance(container, Container):
                container = self.get_container(container)
            return {
                'res': container.logs(),
                'code': 0
            }
        except docker.errors.APIError as exc:
            raise NotFoundError('get_container_logs failed: {}'.format(exc))

    def connect_network_to_service(self, service, network):
        """
        Connect the given network to the given service. To do this, the service is updated with the network.

        Args:
            service: docker.models.services.Service
            network: docker.models.networks.Network

        Returns:
            docker.models.containers.Container

        """
        try:
            wait_on_service_replication(self._docker, service)
            wait_on_service_container_status(self, service)

            n = network if isinstance(network, Network) else self.get_network(network)
            s = service if isinstance(service, Service) else self.get_service(service)
        except (docker.errors.NotFound, docker.errors.APIError, NotFoundError) as exc:
            raise DeploymentError('Entity not found: {}'.format(exc))

        BuiltIn().log('Connecting network {} to service {}...'.format(n.name, s.name),
                      level='INFO',
                      console=Settings.to_console)
        try:
            return self.update_service(s, networks=[n.name])
        except docker.errors.APIError as exc:
            raise DeploymentError('Could not connect network to container: {}'.format(exc))

    def update_service(self, service, **kwargs):
        """
        Update a service using the map of configuration values.

        Args:
            service: docker.models.services.Service
            **kwargs: any parameters available for updating a service

        Returns:
            Container: Instance of Container

        """
        assert isinstance(service, Service)
        try:
            current_instances = frozenset(self.get_containers_for_service(service))
            service.update(**kwargs)
            return self._wait_on_service_update(service, current_instances)
        except docker.errors.APIError as exc:
            raise DeploymentError('Could not update service {}: {}'.format(service.name, exc))

    def _wait_on_service_update(self, service, current_instances=None):
        """
        After a service is updated, we wait for at least one new container instance with the updated configuration to be
        available.

        Args:
            service: service instance
            current_instances: list of containers belonging to the service currently

        Returns:
            Container: Container instance with the updated configuration

        """
        service = service if isinstance(service, Service) else self.get_service(service)
        BuiltIn().log(
            'Waiting for service to update {}...'.format(service.name if isinstance(service, Service) else ''),
            level='DEBUG', console=Settings.to_console)

        # wait for the update to take place
        wait_on_service_replication(self._docker, service)
        wait_on_service_container_status(self, service, current_instances)
        c = self.get_containers_for_service(service)[0]
        wait_on_container_status(self, c)
        return c

    def connect_volume_to_service(self, service, volume):
        """
        Connect a given volume to a given service.
        In case the volume is already connect, just return the service.

        Args:
            service: docker.models.services.Service
            volume: docker.models.volumes.Volume

        Returns:
            Container

        """
        if not volume:
            raise DeploymentError('You must provide a volume to connect it to a service.')
        if not service:
            raise DeploymentError('You must provide a service to connect a volume.')

        try:
            wait_on_service_replication(self._docker, service)
            wait_on_service_container_status(self, service)

            v = volume if isinstance(volume, Volume) else self.get_volume(volume)
            s = service if isinstance(service, Service) else self.get_service(service)
        except (docker.errors.NotFound, docker.errors.APIError, NotFoundError) as exc:
            raise DeploymentError('Entity not found: {}'.format(exc))

        try:
            attrs = getattr(s, 'attrs')
            mounts = attrs.get('Spec', {}).get('TaskTemplate', {}).get('ContainerSpec', {}).get('Mounts', [])
            for mount in mounts:
                if v.name in mount.get('Source', {}):
                    return self.get_containers_for_service(s)[0]
        except (AttributeError, ValueError):
            pass

        BuiltIn().log('Connecting volume {} to service {}...'.format(v.name, s.name),
                      level='INFO',
                      console=Settings.to_console)
        try:
            return self.update_service(s, mounts=['{}:/goss:ro'.format(v.name)])
        except docker.errors.APIError as exc:
            raise DeploymentError('Could not connect network to container: {}'.format(exc))

    def clean_networks(self):
        """
        Helper method. Sometimes the list of networks is in an unclean state and requires manual cleanup.

        Returns:
            None

        """
        self._docker_api.prune_networks()

    def deploy_stack(self, descriptor, name):
        """
        Deploy a docker-compose.yml file on a Docker Swarm.

        Args:
            descriptor: str
            name: str

        Returns:
            True

        """
        assert name, "name is required for deploy_stack"
        assert descriptor, "descriptor is required for deploy_stack"
        res = self._dispatch(['stack', 'deploy', '-c', descriptor, name])
        if res.stderr:
            raise DeploymentError(res.stderr)
        return True

    def undeploy_stack(self, name):
        """
        Removes a docker-compose.yml deployment from a Docker Swarm

        Args:
            name: str

        Returns:
            ProcessResult

        """
        a = self._dispatch(['stack', 'rm', name])
        self.clean_networks()
        return a

    def get_network(self, name):
        """
        Retrieves a network by name

        Args:
            name: str

        Returns:
            docker.models.networks.Network

        """
        try:
            return self._docker.networks.get(name)
        except docker.errors.NotFound as exc:
            raise NotFoundError(exc)

    def get_or_create_network(self, name, driver='overlay'):
        """
        Retrieves a network by name and creates it if it does not yet exist.
        The network driver defaults to 'overlay'.

        Args:
            name: str
            driver: str

        Returns:
            docker.models.networks.Network

        """
        try:
            return self._docker.networks.create(
                name=name,
                driver=driver,
                scope='swarm' if driver == 'overlay' else 'local',
                attachable=True)
        except docker.errors.APIError as exc:
            if 'already exists' in exc.explanation:
                return self._docker.networks.get(name)
            else:
                raise
        # self._dispatch(['network', 'create', name, '--attachable', '--scope', 'swarm'])
        # return self.get_network(name)

    def delete_network(self, name):
        """
        Deletes a network.

        Args:
            name: str

        Returns:
            None

        """
        n = self._docker.networks.get(name)
        if n.containers:
            for c in n.containers:
                n.disconnect(c)

        n.remove()

    def delete_container(self, name):
        """
        Deletes a container.

        Args:
            name: str

        Returns:
            None

        """
        try:
            c = self._docker.containers.get(name)
            c.remove()
        except (docker.errors.APIError, docker.errors.NotFound) as exc:
            raise DeploymentError('Could not delete container {}: exc'.format(name, exc))

    def create_volume(self, name):
        """
        Creates a volume.

        Args:
            name: str

        Returns:
            docker.models.volumes.Volume

        """
        try:
            return self._docker.volumes.create(name)
        except docker.errors.NotFound:
            raise DeploymentError('Could not create volume {}'.format(name))
        except docker.errors.APIError as exc:
            raise DeploymentError('Could not create volume {}: {}'.format(name, exc))

    def delete_volume(self, name):
        """
        Deletes a volume.

        Args:
            name: str

        Returns:
            None

        """
        try:
            v = self._docker.volumes.get(name)
            v.remove(force=True)
        except docker.errors.NotFound:
            raise DeploymentError('Could not remove volume {}: Not found'.format(name))
        except docker.errors.APIError as exc:
            raise DeploymentError('Could not remove volume {}: {}'.format(name, exc))

    def get_volume(self, name):
        """
        Retrieves a volume by name.

        Args:
            name: str

        Returns:
            docker.models.volumes.Volume

        """
        try:
            return self._docker.volumes.get(name)
        except (docker.errors.NotFound, docker.errors.APIError) as exc:
            raise DeploymentError('Could not find volume {}: {}'.format(name, exc if exc else ''))

    def add_data_to_volume(self, volume, path):
        """
        Adds data to a volume. For that, it mounts the volume to a busybox container, copies the files from the local
        file system and removes the container.

        Args:
            volume: str - name of the volume
            path: str - local path with the files to be copied

        Returns:
            None

        """
        try:
            self._kill_and_delete_container(self.helper)
        except docker.errors.NotFound:
            pass

        BuiltIn().log('Copying {} to {}...'.format(path, volume),
                      level='INFO',
                      console=Settings.to_console)
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
        """
        Retrieves a list of files on a volume. Tailored for goss at the moment.
        For that, a `ls /data` is executed on the volume.

        Args:
            volume: str - name of the volume

        Returns:
            str

        """
        try:
            self.get_volume(volume)
        except DeploymentError as exc:
            raise exc

        res = self._dispatch(['run', '--rm', '-v', '{}:/data'.format(volume), 'busybox', 'ls', '/data'])
        assert len(res.stderr) == 0

        return res

    def get_or_create_sidecar(self, image='busybox', command='true', name='', volumes=None, network=None):
        """
        Helper method for run_sidecar().
        A container is created with the provided parameters.
        An existing sidecar with an identical name is removed first.

        Args:
            image: str - image
            command: str - command
            name: str - name
            volumes:
            network:

        Returns:
            docker.models.containers.Container

        """

        # Do not reuse for the moment being as we are reading stdout and the stdout history is not reset between
        # different testtools runs. We end up with multiple json objects we cannot easily decode for now
        # # try to get an existing sidecar
        # if name:
        #     try:
        #         c = self._docker.containers.get(name)
        #         if isinstance(c, Container):
        #             logger.console('Found container {}. Re-using it as sidecar.'.format(name))
        #             return c
        #     except docker.errors.NotFound:
        #         pass

        # remove existing sidecar
        try:
            self.delete_container(name)
            BuiltIn().log('Removing existing sidecar container {}'.format(name),
                          level='DEBUG',
                          console=Settings.to_console
                          )
        except DeploymentError:
            pass

        try:
            self.get_or_pull_image(image)
            BuiltIn().log('Creating sidecar container: name={}, image={}, command={}, volumes={}, networks={}'.format(
                name, image, command, volumes, network),
                level='INFO',
                console=Settings.to_console)
            return self._docker.containers.create(name=name if name else None,
                                                  image=image,
                                                  command=command,
                                                  auto_remove=False,
                                                  volumes=volumes,
                                                  network=network,
                                                  tty=True)
        except docker.errors.APIError as exc:
            raise DeploymentError('Could not deploy sidecar: {}'.format(exc))
        except NotFoundError as exc:
            raise DeploymentError('Image {} not found: {}'.format(image if image else '', exc))
        except docker.errors.ContainerError as exc:
            BuiltIn().log('get_or_create_sidecar(): {}'.format(exc),
                          level='INFO',
                          console=Settings.to_console)
            raise DeploymentError('Error: {}'.format(exc))

    def get_or_pull_image(self, image):
        """
        Retrieves an image from hub.docker.com.

        Args:
            image: str - image name

        Returns:
            None

        """
        try:
            self._docker.images.get(image)
        except docker.errors.ImageNotFound:
            try:
                logger.console(
                    'Fetching sidecar image...')
                self._docker.images.pull(image)
            except docker.errors.ImageNotFound as exc:
                raise NotFoundError('Image {} not found: {}'.format(image, exc))

    def run_sidecar(self, name='', sidecar=None, image='busybox', command='true', volumes=None, network=None):
        """
        Run a sidecar container with the specified parameters. It waits for the command to finish and returns stdout.
        If stderr is not empty, a DeploymentError is raised with stderr.

        Args:
            name: str - name of the container
            sidecar: docker.models.containers.Container
            image: str - name of the image
            command: str - command to run
            volumes:
            network:

        Returns:
            str - stdout

        """

        # maybe try this:
        # docker service create --network dockercoins_default --name set_breakpoint \
        #        --constraint node.hostname==$HOSTNAME alpine sleep 1000000000
        #
        #
        #

        try:
            if not sidecar:
                sidecar = self.get_or_create_sidecar(image, command, name, volumes, network)
            wait_on_container_status(self, sidecar, ['Created', 'Exited'])
            sidecar.start()
            sidecar.wait()
            stdout = sidecar.logs(stdout=True, stderr=False) or ''
            stderr = sidecar.logs(stdout=False, stderr=True) or ''

            # BuiltIn().log(stdout, level='DEBUG', console=Settings.to_console)

            if stderr:
                raise DeploymentError('Found stderr: {}'.format(stderr))
            return {
                'code': 0,
                'res': stdout
            }
        except docker.errors.NotFound:
            raise DeploymentError('Sidecar {} not found.'.format(sidecar if sidecar else 'None'))
        except docker.errors.APIError as exc:
            if 'executable file not found' in exc.explanation:
                raise DeploymentError('Could not run command: {}'.format(exc))
            else:
                raise DeploymentError('Could not run sidecar: {}'.format(exc))
        except docker.errors.ContainerError as exc:
            BuiltIn().log('run_sidecar(): {}'.format(exc),
                          level='DEBUG',
                          console=Settings.to_console)
            raise DeploymentError('Error: {}'.format(exc))
        finally:
            self._kill_and_delete_container(sidecar)

    def _dispatch(self, options, project_options=None, returncode=0):
        """
        Helper method to run Docker commands that are not available via the API.

        Args:
            options:
            project_options:
            returncode:

        Returns:

        """
        project_options = project_options or []
        o = project_options + options
        proc = start_process(self.base_dir, o)
        return wait_on_process(proc, returncode=returncode)

    def find_stack(self, deployment_name):
        """
        Find a stack by name.

        Args:
            deployment_name: str - name of the stack

        Returns:
            True

        """
        res = self._dispatch(['stack', 'ps', deployment_name, '--format', '" {{ .Name }}"'])

        if deployment_name not in res.stdout.strip('\n\r'):
            raise DeploymentError('Stack {} not found.'.format(deployment_name))
        return True

    def put_file(self, entity, file_to_transfer='', destination='/', filename=None):
        """
        Copy a file onto a running container.

        Args:
            entity: docker.models.containers.Container
            file_to_transfer: local file object
            destination: path to the destination
            filename: destination file name

        Returns:
            None

        """
        if not os.path.isfile(file_to_transfer):
            raise NotFoundError('File {} not found'.format(file_to_transfer))

        if isinstance(entity, Container):
            entity = entity.name
        filename = filename or os.path.basename(file_to_transfer)
        BuiltIn().log('Putting file {} on {}'.format(filename, entity),
                      level='INFO',
                      console=Settings.to_console)
        with open(file_to_transfer, 'r') as f:
            content = f.read()
            self._send_file(content, destination, entity, filename)

    def _send_file(self, content, destination, entity, filename):
        """
        Helper method for put_file().
        Creates a temporary tar file with the specified content.

        Args:
            content:
            destination:
            entity:
            filename:

        Returns:

        """
        to_send = Archive('w').add_text_file(filename, content).close()
        try:
            res = self._docker_api.put_archive(entity, destination, to_send.buffer)
            assert res
            # self.file_exists(entity, filename)
        except docker.errors.APIError as exc:
            raise DeploymentError(exc)

    def get_file(self, entity, path, filename):
        """
        Retrieves a file from a container.

        Args:
            entity: docker.models.containers.Container
            path: path to file
            filename: filename on container

        Returns:
            Archive

        """
        try:
            strm, stat = self._docker_api.get_archive(entity, '{}/{}'.format(path, filename))
        except docker.errors.APIError as exc:
            raise DeploymentError(exc)

        return Archive('r', strm.read()).get_text_file(filename)

    def get_services(self, stack):
        """
        Retrieve services for a stack.

        Args:
            stack: str - name of deployment

        Returns:
            [Service]

        """
        try:
            return self._docker.services.list(filters={'name': '{}_'.format(stack)})
        except docker.errors.APIError as exc:
            raise DeploymentError('Could not get services for {}: {}'.format(stack, exc))

    def _kill_and_delete_container(self, name):
        """
        Removes a container.

        Args:
            name: str - name of container

        Returns:
            None

        """
        try:
            c = self._docker.containers.get(name) if isinstance(name, basestring) else name
            if hasattr(c, 'status') and lower(c.status) == 'running':
                c.kill()
            if isinstance(c, Container):
                c.remove()
        except docker.errors.APIError as exc:
            if 'No such container' in exc.explanation:
                pass
            elif 'is not running' in exc.explanation:
                pass
            else:
                raise
