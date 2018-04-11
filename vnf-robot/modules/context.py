import collections

from exc import NotFoundError, SetupError
SUT = collections.namedtuple('sut', 'target_type, target, service_id')


def set_context(instance, context_type=None, context=None):
    context_types = ['application', 'service', 'node', 'network']

    service_id = '{}_{}'.format(instance.deployment_name, context)

    if context_type not in context_types:
        raise SetupError('Invalid context given. Must be {}'.format(context_types))
    if context is None:
        raise SetupError('No context given.')

    # Check that service exists
    try:
        instance.docker_controller.get_service(service_id)
    except NotFoundError as exc:
        raise

    return SUT(context_type, context, service_id)