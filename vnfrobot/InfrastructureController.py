from abc import ABCMeta, abstractmethod


class InfrastructureController:
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    # Deployment management
    @abstractmethod
    def deploy_stack(self, descriptor, name):
        raise NotImplementedError('Needs implementation.')

    @abstractmethod
    def find_stack(self, deployment_name):
        raise NotImplementedError('Needs implementation.')

    @abstractmethod
    def undeploy_stack(self, name):
        raise NotImplementedError('Needs implementation.')

    @abstractmethod
    def get_node(self, node_id):
        raise NotImplementedError('Needs implementation.')

    # Services management
    @abstractmethod
    def get_service(self, service):
        raise NotImplementedError('Needs implementation.')

    @abstractmethod
    def get_services(self, stack):
        raise NotImplementedError('Needs implementation.')

    @abstractmethod
    def update_service(self, service, **kwargs):
        raise NotImplementedError('Needs implementation.')

    @abstractmethod
    def connect_network_to_service(self, service, network):
        raise NotImplementedError('Needs implementation.')

    @abstractmethod
    def connect_volume_to_service(self, service, volume):
        raise NotImplementedError('Needs implementation.')

    # Containers management
    @abstractmethod
    def get_container(self, container):
        raise NotImplementedError('Needs implementation.')

    @abstractmethod
    def get_containers(self):
        raise NotImplementedError('Needs implementation.')

    @abstractmethod
    def get_container_config(self, entity, key):
        raise NotImplementedError('Needs implementation.')

    @abstractmethod
    def get_containers_for_service(self, service, state):
        raise NotImplementedError('Needs implementation.')

    @abstractmethod
    def get_or_create_sidecar(self):
        raise NotImplementedError('Needs implementation.')

    @abstractmethod
    def run_sidecar(self):
        raise NotImplementedError('Needs implementation.')

    @abstractmethod
    def execute(self):
        raise NotImplementedError('Needs implementation.')

    @abstractmethod
    def get_or_pull_image(self, image):
        raise NotImplementedError('Needs implementation.')

    # Files management
    @abstractmethod
    def get_file(self, entity, path, filename):
        raise NotImplementedError('Needs implementation.')

    @abstractmethod
    def put_file(self, entity, file_to_transfer, destination, filename):
        raise NotImplementedError('Needs implementation.')

    @abstractmethod
    def list_files_on_volume(self, volume):
        raise NotImplementedError('Needs implementation.')

    # Volumes management
    @abstractmethod
    def delete_volume(self, name):
        raise NotImplementedError('Needs implementation.')

    @abstractmethod
    def create_volume(self, name):
        raise NotImplementedError('Needs implementation.')

    @abstractmethod
    def get_volume(self, name):
        raise NotImplementedError('Needs implementation.')

    @abstractmethod
    def add_data_to_volume(self, volume, path):
        raise NotImplementedError('Needs implementation.')

    # Networks management
    @abstractmethod
    def delete_network(self, name):
        raise NotImplementedError('Needs implementation.')

    @abstractmethod
    def get_or_create_network(self, name, driver):
        raise NotImplementedError('Needs implementation.')

    @abstractmethod
    def get_network(self, name):
        raise NotImplementedError('Needs implementation.')