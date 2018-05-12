import pytest

from exc import SetupError, ValidationError
from fixtures.test_data_File import file_target_test_data_pass, file_target_test_data_fail, file_test_data
from tools.data_structures import SUT
from utils import set_test_data


@pytest.mark.target
@pytest.mark.kw_file
def test__context__invalid__fail(file_with_instance):
    with pytest.raises(SetupError, match='No SUT'):
        file_with_instance.validate()


@pytest.mark.target
@pytest.mark.kw_file
@pytest.mark.parametrize('test', file_target_test_data_pass)
def test__validate__pass(file_with_instance, sut, test):
    e = file_with_instance
    e.instance.sut = sut

    set_test_data(e, test)
    e.validate()


@pytest.mark.target
@pytest.mark.kw_file
@pytest.mark.parametrize('test', file_target_test_data_fail)
def test__validate__fail(file_with_instance, sut, test):
    e = file_with_instance
    e.instance.sut = sut

    set_test_data(e, test)
    with pytest.raises(ValidationError):
        e.validate()


@pytest.mark.target
@pytest.mark.kw_file
@pytest.mark.parametrize('test, data, expected, yaml', file_test_data)
def test__prepare_transform__pass(file_with_instance, sut, test, data, expected, yaml, mocker):
    e = file_with_instance
    e.instance.sut = sut

    set_test_data(e, test.get('test'))
    e._prepare_transform()

    assert e.data == data.get('data')


@pytest.mark.target
@pytest.mark.kw_file
@pytest.mark.integration
@pytest.mark.parametrize('test', file_target_test_data_pass)
def test__run__pass(file_with_instance, stack, test):
    e = file_with_instance

    name, path, success = stack
    e.instance.deployment_name = name
    e.instance.sut = SUT('service', 'sut', '{}_sut'.format(name))

    set_test_data(e, test)

    e.run_test()
