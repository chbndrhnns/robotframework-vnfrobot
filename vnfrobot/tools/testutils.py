import re
from string import lower

import exc
from tools.matchers import string_matchers
from tools.validators import Validator


def get_truth(inp, relate, val=None):
    """
    Perform a comparison based on `relate`

    Args:
        inp: str - input value
        relate:
        val:

    Returns:

    """
    if inp is None:
        raise exc.ValidationError('get_truth: actual value not set.')
    if not relate:
        raise exc.ValidationError('get_truth: matcher not set.')

    inp = inp.strip('\n\t ') if isinstance(inp, basestring) else inp

    # empty/not empty is not part of the operators. suite
    if isinstance(relate, basestring) and 'is empty' in relate:
        return len(inp) == 0
    if isinstance(relate, basestring) and 'is not empty' in relate:
        return len(inp)

    # from now on, we expect val to be not None
    if val is None:
        raise exc.ValidationError('get_truth: expected value not set.')
    # special case: 'contains' not is not covered by the operator module
    if relate == 'contains_not':
        return val not in inp
    # for operator.contains, the order of arguments is reversed
    if relate.__name__ == 'contains':
        try:
            return relate(inp, val)
        except TypeError as e:
            raise exc.ValidationError(e)

    try:
        inp_integer = int(inp)
        val_integer = int(val)
        return relate(val_integer, inp_integer)
    except ValueError:
        pass
    return relate(val, inp)


def validate_matcher(matchers, limit_to=None):
    if limit_to is None:
        limit_to = []

    invalid = [m for m in matchers if m not in string_matchers.keys()]
    if invalid:
        raise exc.ValidationError('Matchers {} not allowed here.'.format(invalid))

    if limit_to:
        invalid = [m for m in matchers if m not in limit_to]
        if invalid:
            raise exc.ValidationError('Matchers {} not allowed here.'.format(invalid))


def call_validator(entity, validator, context=None, override=None):
    if context is not None:
        v = validator(context=context)
    elif override is not None:
        v = validator(override=override)
    elif override is not None and context is not None:
        v = validator(context=context, override=override)
    else:
        v = validator()
    if isinstance(v, Validator):
        res = v.validate(entity)
        if res:
            return True
        else:
            raise exc.ValidationError('validators.{}: "{}" not valid'.format(v.name, entity))
    else:
        raise TypeError('call_validator must be called with validator callable. Got: {}'.format(entity))


def validate_value(properties, prop, value):
    validator = properties[prop]

    if isinstance(validator.get('values'), list):
        valid = value in properties.get(prop, {}).get('values', {})
        if not valid:
            raise exc.ValidationError(
                'Value "{}" not allowed for {}. Must be any of {}'.format(value, prop, properties[prop]))
    elif isinstance(validator.get('values')(), Validator):
        v = validator.get('values')()
        if not v.validate(value):
            raise exc.ValidationError(
                'Value "{}" not allowed for {}. Must be any of {}'.format(value, prop, v.name))

    return value


def validate_property(properties, raw_prop):
    # Check that the given property is valid
    if not properties.get(raw_prop, None):
        raise exc.ValidationError(
            'Property "{}" not allowed. Must be any of {}'.format(raw_prop, properties.keys()))

    return raw_prop


def validate_against_regex(context, raw_value, regex):
    found = re.search(regex, raw_value)
    if not found:
        raise exc.ValidationError('Value "{}" not valid for {}'.format(raw_value, context))


def validate_port(raw_entity):
    # Check that raw_entity is valid
    # 0 < port <= 65535
    # \d+
    entity = re.search('(\d+)[/]?(\w{,3})?', raw_entity, re.IGNORECASE)
    if not entity:
        raise exc.ValidationError(
            'Port "{}" not valid.'.format(raw_entity))
    port = int(entity.group(1)) if entity else None
    protocol = entity.group(2) if entity.groups is not None else None
    if not (0 < port <= 65535):
        raise exc.ValidationError(
            'Port "{}" not valid. Must be between 1 and 65535'.format(port))
    if len(protocol) > 0 and lower(protocol) not in ['tcp', 'udp']:
        raise exc.ValidationError(
            'Protocol "{}" not valid. Only udp and tcp are supported'.format(protocol))

    return port, protocol


class Result:
    def __init__(self):
        pass

    PASS = 0
    FAIL = 1

    map = {'PASS': 0, '0': 'PASS', '1': 'FAIL', 'FAIL': 1}

    @classmethod
    def get(cls, key):
        return cls.map.get(str(key))


regex_method = re.compile('test__(\w+)__\w+')


# noinspection PyUnusedLocal
def run_keyword_tests(test_instance, tests=None, setup=None, expected_result=Result.PASS, expected_message=None):
    # caller_name = inspect.stack()[1][3]
    # TODO: verify that the expected method is called
    # test_name = regex_method.findall(caller_name)[0]

    run_count = 0
    context = test_instance.tests
    for t in tests:
        run_count += 1
        test = context.create(u'Expect {}: {}'.format(Result.get(expected_result), t))
        test.keywords.append(t)

    result = test_instance.run(output=None)

    if expected_result is Result.FAIL:
        assert run_count == result.statistics.total.all.failed, 'Expected failure count does not match actual failure count.'
    if expected_result is Result.PASS:
        assert run_count == result.statistics.total.all.passed, 'Expected pass count does not match actual pass count.'

    if expected_message:
        for result in result.suite.tests:
            test_instance.assertIn(expected_message, result.message)
