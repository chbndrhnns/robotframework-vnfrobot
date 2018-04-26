from pytest import fixture

from tools.data_structures import SUT


@fixture
def goss_sut_service(stack, containers):
    return SUT(
        target_type='service',
        target=containers[0].name,
        service_id=stack[0]
    )