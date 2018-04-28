import exc


def validate(instance):
    allowed_context = ('node',)

    if instance.sut.target_type not in allowed_context:
        raise exc.SetupError('Context type "{}" not allowed.'.format(instance.sut.target_type))

    return dict([('OS_USERNAME', 'admin'), ('OS_AUTH_URL', 'http://localhost:5000/api')])