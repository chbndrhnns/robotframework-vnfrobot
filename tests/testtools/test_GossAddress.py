import pytest
from ruamel import yaml

from fixtures.test_data_Address import addresses_test_data
from tools.goss.GossAddr import GossAddr


@pytest.mark.parametrize('test, data, expected, yaml', addresses_test_data)
def test__GossAddr__apply_mappings__pass(test, data, expected, yaml):
    g = GossAddr(data.get('data'))

    g.apply_mappings(g)

    expected = expected.get('with_mappings')
    actual = g.mapped

    assert actual == expected


@pytest.mark.parametrize('test, data, mapped, out', addresses_test_data)
def test__GossAddr__transform__pass(test, data, mapped, out):
    g = GossAddr(data.get('data'))

    g.transform(g)

    expected = yaml.safe_load(out.get('expected_yaml'))
    actual = yaml.safe_load(g.out)

    assert actual == expected
