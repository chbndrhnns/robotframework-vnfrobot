from robot.libraries.BuiltIn import BuiltIn

from tools.data_structures import SUT
from exc import NotFoundError, SetupError
from tools.wait_on import wait_on_container_status, wait_on_service_replication, wait_on_service_container_status


def _generate_sidecar_name(service_id):
    return 'robot_sidecar_for_{}'.format(service_id)


def set_context(instance, context_type=None, context=None):
    controller = instance.docker_controller
    context_types = ['application', 'service', 'node', 'network']

    service_id = '{}_{}'.format(instance.deployment_name, context)
    BuiltIn().log('Context: Using service_id {}'.format(service_id), level='INFO', console=True)

    if context_type not in context_types:
        raise SetupError('Invalid context given. Must be {}'.format(context_types))
    if not context:
        raise SetupError('No context given.')

    # Check that service exists
    try:
        service = controller.get_service(service_id)
    except NotFoundError as exc:
        raise SetupError('Service {} not found in deployment {}'.format(context, instance.deployment_name))

    if context_type == 'network':
        try:
            context = _prepare_network_context(controller, service_id)
        except Exception:
            raise
    elif context_type == 'service':
        try:
            context = _prepare_service_context(controller, instance, service_id)
        except NotFoundError:
            raise SetupError('Context target {} not found in deployment {}'.format(context, instance.deployment_name))

    if not context:
        raise SetupError('Context target is empty. This indicates a bug.')

    return SUT(context_type, context, service_id)


def _prepare_service_context(controller, instance, service_id):
    ctl = instance.docker_controller._docker
    # find a container for the service and wait until its ready
    wait_on_service_container_status(ctl, service_id)

    # attach the goss volume to the service
    controller.connect_volume_to_service(service_id, instance.test_volume)

    # wait for the update to take place
    containers = instance.docker_controller.get_containers_for_service(service_id)
    context = containers[0].name
    wait_on_container_status(instance.docker_controller._docker, context)

    return context


def _prepare_network_context( controller, service_id):
    network = controller.get_or_create_network(_generate_sidecar_name(service_id))
    sidecar = controller.get_or_create_sidecar(
        image='busybox',
        command='',
        name=_generate_sidecar_name(service_id),
        volumes='',
        networks=''
    )

    return network.name
