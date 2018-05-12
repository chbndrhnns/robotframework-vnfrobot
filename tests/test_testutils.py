import pytest

from exc import ValidationError
from tools import validators
from tools.testutils import get_truth, call_validator
import operator

not_valid_match = 'not valid'


def test__get_truth__empty_inp__fail():
    inp = None
    relate = operator.contains
    val = 'cd'

    with pytest.raises(ValidationError):
        get_truth(inp, relate, val)


@pytest.mark.parametrize('data', ['', '\n', ' '])
def test__get_truth__is_empty__pass(data):
    relate = 'is empty'

    assert get_truth(data, relate, None)


@pytest.mark.parametrize('data', ['a', ' a', '\na'])
def test__get_truth__is_empty__fail(data):
    relate = 'is empty'

    assert not get_truth(data, relate, None)


@pytest.mark.parametrize('data', ['a', ' a', '\na'])
def test__get_truth__is_not_empty__pass(data):
    relate = 'is not empty'

    assert get_truth(data, relate, None)


@pytest.mark.parametrize('data', ['', '\n', ' '])
def test__get_truth__is_not_empty__fail(data):
    relate = 'is not empty'

    assert not get_truth(data, relate, None)


def test__get_truth__contains_string():
    inp = 'abcd efg'
    relate = operator.contains
    val = 'cd'

    res = get_truth(inp, relate, val)

    assert res


def test__get_truth__contains_list():
    inp = ['a', 'ab', 'abc']
    relate = operator.contains
    val = 'abc'

    res = get_truth(inp, relate, val)

    assert res


def test__get_truth__contains_not():
    inp = ['a', 'ab', 'abc']
    relate = 'contains_not'
    val = 'def'

    res = get_truth(inp, relate, val)

    assert res


def test__validate_entity__url__fail():
    inp = 'http://www.google.d'
    url_validator = validators.Url

    with pytest.raises(ValidationError):
        call_validator(inp, url_validator)


def test__validate_entity__url__pass():
    inp = 'http://www.google.de'
    url_validator = validators.Url

    assert call_validator(inp, url_validator)


def test__validate_entity__domain__fail():
    inp = 'www.google.d'
    url_validator = validators.Domain

    with pytest.raises(ValidationError):
        call_validator(inp, url_validator)


def test__validate_entity__domain__pass():
    inp = 'www.google.de'
    url_validator = validators.Domain

    assert call_validator(inp, url_validator)


def test__validate_entity__domain__override__pass():
    inp = 'www.google.de'
    override = ['awesome']
    url_validator = validators.Domain

    assert call_validator(inp, url_validator, override=override)


def test__validate_entity__service__pass(sut):
    inp = 'sut'
    validator = validators.Service

    assert call_validator(inp, validator, sut)


def test__validate_entity__service__fail(sut):
    inp = 'sutnotexist'
    validator = validators.Service

    with pytest.raises(ValidationError):
        call_validator(inp, validator, sut)


def test__validate_entity__service__no_context__fail():
    inp = 'sutnotexist'
    validator = validators.Service

    with pytest.raises(ValidationError):
        call_validator(inp, validator, '')


def test__validate_entity__context__pass():
    inp = 'service'
    validator = validators.Context

    call_validator(inp, validator, ['service', 'network'])


def test__validate_entity__context__fail():
    inp = 'service'
    validator = validators.Context

    with pytest.raises(ValidationError, match=not_valid_match):
        call_validator(inp, validator, ['application'])


def test__validate_entity__property__pass():
    inp = 'a'
    validator = validators.Property

    call_validator(inp, validator, {'a': {}})


def test__validate_entity__property__no_dict__fail():
    inp = 'a'
    validator = validators.Property

    with pytest.raises(ValidationError, match='dict'):
        call_validator(inp, validator, ['application'])


def test__validate_entity__property__fail():
    inp = 'a'
    validator = validators.Property

    with pytest.raises(ValidationError, match=not_valid_match):
        call_validator(inp, validator, {'b': {}})


def test__validate_entity__matcher__pass():
    inp = 'is not'
    validator = validators.InList

    call_validator(inp, validator, ['is not'])


def test__validate_entity__matcher__no_list__fail():
    inp = 'a'
    validator = validators.InList

    with pytest.raises(ValidationError, match='list'):
        call_validator(inp, validator, 'application')


def test__validate_entity__matcher__fail():
    inp = 'is'
    validator = validators.InList

    with pytest.raises(ValidationError, match=not_valid_match):
        call_validator(inp, validator, ['contains'])


def test__validate_entity__regex__pass():
    inp = 'isnot'
    validator = validators.Regex

    call_validator(inp, validator, '\S+')


def test__validate_entity__regex__no_basestring__fail():
    inp = 'a'
    validator = validators.Regex

    with pytest.raises(ValidationError, match='basestring'):
        call_validator(inp, validator, [''])


def test__validate_entity__regex__no_regex__fail():
    inp = 'a'
    validator = validators.Regex

    with pytest.raises(ValidationError, match='regex'):
        call_validator(inp, validator, '[')


def test__validate_entity__regex__fail():
    inp = 'bla a '
    validator = validators.InList

    with pytest.raises(ValidationError, match=not_valid_match):
        call_validator(inp, validator, ['\S+'])


@pytest.mark.parametrize('port', ['80', 80, 65000])
def test__validate_entity__port__pass(port):
    validator = validators.Port

    call_validator(port, validator)


@pytest.mark.parametrize('port', ['0', 65537, "a"])
def test__validate_entity__port__fail(port):
    validator = validators.Port

    with pytest.raises(ValidationError, match=not_valid_match):
        call_validator(port, validator)


@pytest.mark.parametrize('perm', ['executable', '0755', 0600])
def test__validate_entity__chmod__pass(perm):
    validator = validators.Permission

    assert call_validator(perm, validator)


@pytest.mark.parametrize('perm', ['executb', '12b'])
def test__validate_entity__chmod__fail(perm):
    validator = validators.Permission

    with pytest.raises(ValidationError, match=not_valid_match):
        call_validator(perm, validator)
