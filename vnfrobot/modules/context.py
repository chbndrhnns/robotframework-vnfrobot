from tools.data_structures import SUT
from exc import NotFoundError, SetupError
from tools.wait_on import wait_on_container_status


def _generate_sidecar_name(service_id):
    return 'robot_sidecar_for_{}'.format(service_id)


def set_context(instance, context_type=None, context=None):
    controller = instance.docker_controller
    context_types = ['application', 'service', 'node', 'network']

    service_id = '{}_{}'.format(instance.deployment_name, context)

    if context_type not in context_types:
        raise SetupError('Invalid context given. Must be {}'.format(context_types))
    if context is None:
        raise SetupError('No context given.')

    # Check that service exists
    try:
        service = controller.get_service_for_stack(service_id)
    except NotFoundError as exc:
        raise SetupError('Service {} not found in deployment {}'.format(context, instance.deployment_name))

    if context_type == 'network':
        try:
            network = controller.get_or_create_network(_generate_sidecar_name(service_id))

            sidecar = controller.get_or_create_sidecar(
                image='busybox',
                command='',
                name=_generate_sidecar_name(service_id),
                volumes='',
                networks=''
            )
            context = network.name
        except Exception:
            raise
    elif context_type == 'service':
        try:
            # find a container for the service and wait until its ready
            containers = instance.docker_controller.get_containers_for_service(service_id)
            context = containers[0].name
            wait_on_container_status(instance.docker_controller._docker, context)

            # attach the goss volume to the service
            controller.connect_volume_to_service(service, instance.test_volume)

        except NotFoundError:
            raise SetupError('Context target {} not found in deployment {}'.format(context, instance.deployment_name))

    return SUT(context_type, context, service_id)
