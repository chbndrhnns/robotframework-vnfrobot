import pytest
from ruamel import yaml

from fixtures.test_data_File import file_test_data
from tools.goss.GossFile import GossFile


@pytest.mark.kw_file
@pytest.mark.parametrize('test, data, expected, yaml', file_test_data)
def test__GossFile__apply_mappings__pass(test, data, expected, yaml):
    g = GossFile(data.get('data'))

    actual = g.apply_mappings(g)
    expected = expected.get('with_mappings')

    assert actual == expected


@pytest.mark.kw_file
@pytest.mark.parametrize('test, data, mapped, out', file_test_data)
def test__GossFile__transform__pass(test, data, mapped, out):
    g = GossFile(data.get('data'))

    g.transform_to_goss(g)

    expected = yaml.safe_load(out.get('expected_yaml'))
    actual = yaml.safe_load(g.out)

    assert actual == expected
