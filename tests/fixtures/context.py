from pytest import fixture


@fixture
def application_context():
    return 'application'


@fixture
def service_context():
    return 'service'


@fixture
def service_context():
    return 'service'


@fixture
def network_context():
    return 'network'
