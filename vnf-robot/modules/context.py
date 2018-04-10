import collections

import exc

SUT = collections.namedtuple('sut', 'target_type, target')


def set_context(context_type=None, context=None):
    context_types = ['application', 'service', 'node', 'network']

    if context_type not in context_types:
        raise exc.SetupError('Invalid context given. Must be {}'.format(context_types))
    if context is None:
        raise exc.SetupError('No context given.')

    return SUT(context_type, context)