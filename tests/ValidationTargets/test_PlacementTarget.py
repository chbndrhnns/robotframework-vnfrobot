import pytest

from exc import SetupError, ValidationError
from fixtures.test_data_Placement import placement_target_test_data, placement_target_test_data_fail
from utils import set_test_data


def test__context__invalid__fail(placement_with_instance):
    with pytest.raises(SetupError, match='No SUT'):
        placement_with_instance.validate()


@pytest.mark.parametrize('test', placement_target_test_data)
def test__validate__pass(placement_with_instance, sut, test):
    e = placement_with_instance
    e.instance.sut = sut

    set_test_data(e, test.get('test'))
    e.validate()


@pytest.mark.parametrize('test', placement_target_test_data_fail)
def test__validate__fail(placement_with_instance, sut, test):
    e = placement_with_instance
    e.instance.sut = sut

    set_test_data(e, test.get('test'))
    with pytest.raises(ValidationError):
        e.validate()
