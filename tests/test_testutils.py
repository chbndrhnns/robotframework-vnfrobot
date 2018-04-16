from tools.testutils import get_truth, validate_entity, Url, Domain
import operator


def test__get_truth__contains_string():
    inp = 'abcd efg'
    relate = operator.contains
    val = 'cd'

    res = get_truth(inp, relate, val)

    assert res == True


def test__get_truth__contains_list():
    inp = ['a', 'ab', 'abc']
    relate = operator.contains
    val = 'abc'

    res = get_truth(inp, relate, val)

    assert res == True


def test__get_truth__contains_not():
    inp = ['a', 'ab', 'abc']
    relate = 'contains_not'
    val = 'def'

    res = get_truth(inp, relate, val)

    assert res == True


def test__validate_entity__url__fail():
    inp = 'http://www.google.d'
    url_validator = Url

    assert not validate_entity(inp, url_validator)


def test__validate_entity__url__pass():
    inp = 'http://www.google.de'
    url_validator = Url

    assert validate_entity(inp, url_validator)


def test__validate_entity__domain__fail():
    inp = 'www.google.d'
    url_validator = Domain

    assert not validate_entity(inp, url_validator)


def test__validate_entity__domain__pass():
    inp = 'www.google.de'
    url_validator = Domain

    assert validate_entity(inp, url_validator)
