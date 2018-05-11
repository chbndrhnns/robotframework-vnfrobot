from robot.libraries.BuiltIn import BuiltIn

from exc import NotFoundError, SetupError
from tools.wait_on import wait_on_service_container_status


def _generate_sidecar_name(service_id):
    return 'robot_sidecar_for_{}'.format(service_id)


def set_context(instance, context_type=None, context=None):
    context_types = ['application', 'service', 'node', 'network']

    if context_type not in context_types:
        raise SetupError('Invalid context given. Must be {}'.format(context_types))

    instance.update_sut(
        target_type=context_type,
        target=context,
        service_id='{}_{}'.format(instance.deployment_name, context)
    )


# def prepare_context(instance, context_type=None, context=None):
#     controller = instance.docker_controller
#     service_id = instance.sut.service_id
#
#     try:
#         controller.get_service(service_id)
#     except NotFoundError:
#         raise SetupError('Service {} not found in deployment {}'.format(context, instance.deployment_name))
#
#     BuiltIn().log('\nPreparing for context "{}"'.format(context_type), level='In', console=Settings.to_console)
#
#     if context_type == 'network':
#         try:
#             context = _prepare_network_context(controller, service_id)
#         except Exception:
#             raise
#     elif context_type == 'service':
#         try:
#             context = _prepare_service_context(controller, instance, service_id)
#         except NotFoundError:
#             raise SetupError('Context target {} not found in deployment {}'.format(context, instance.deployment_name))
#
#     if not context:
#         raise SetupError('Context target is empty. This indicates a bug.')
#
#     instance.update_sut(target_type=context_type, target=context, service_id=service_id)


# noinspection PyProtectedMember
def _prepare_service_context(controller, instance, service_id):
    ctl = instance.docker_controller._docker
    wait_on_service_container_status(ctl, service_id)

    containers = instance.docker_controller.get_containers_for_service(service_id)

    return containers[0].name


# def _prepare_network_context(controller, service_id):
#     BuiltIn().log('Creating helper network...', level='DEBUG', console=Settings.to_console)
#
#     network = controller.get_or_create_network(_generate_sidecar_name(service_id))
#     sidecar = controller.get_or_create_sidecar(
#         image='busybox',
#         command='',
#         name=_generate_sidecar_name(service_id),
#         volumes='',
#         network=''
#     )
#
#     return network.name
