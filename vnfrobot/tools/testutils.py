import inspect
import re

from string import lower

from robot.libraries.BuiltIn import BuiltIn

import exc
from settings import Settings
from tools.matchers import string_matchers
from tools.validators import Validator
from timeit import default_timer as timer


def get_truth(inp, relate, val):
    # special case: contains not is not covered by the operator module
    if relate == 'contains_not':
        return val not in inp
    # for operator.contains, the order of arguments is reversed
    if relate.__name__ == 'contains':
        return relate(inp, val)

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


def call_validator(entity, validator, context=None):
    if context is not None:
        v = validator(context)
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


def validate_value(properties, property, value):
    validator = properties[property]

    if isinstance(validator.get('values'), list):
        valid = value in properties.get(property, {}).get('values', {})
        if not valid:
            raise exc.ValidationError(
                'Value "{}" not allowed for {}. Must be any of {}'.format(value, property, properties[property]))
    elif isinstance(validator.get('value')(), Validator):
        v = validator.get('value')()
        if not v.validate(value):
            raise exc.ValidationError(
                'Value "{}" not allowed for {}. Must be any of {}'.format(value, property, v.name))

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


def _add_host_context(self, suite=None, host=None):
    if suite is None:
        return None
    if host is None:
        return None

    context = 'Set context to {}'.format(host)
    return suite.keywords.create(context, type='setup')


def run_keyword_tests(test_instance, tests=None, setup=None, expected_result=Result.PASS, expected_message=None):
    caller_name = inspect.stack()[1][3]
    # TODO: verify that the expected method is called
    test_name = regex_method.findall(caller_name)[0]

    run_count = 0
    context = test_instance.suite.tests
    for t in tests:
        run_count += 1
        with test_instance.subTest(test=t):
            test = context.create(u'Expect {}: {}'.format(Result.get(expected_result), t))
            test.keywords.append(t)

    result = test_instance.suite.run(output=None)

    if expected_result is Result.FAIL:
        test_instance.assertEqual(run_count, result.statistics.total.all.failed,
                                  'Expected failure count does not match actual failure count.')
    if expected_result is Result.PASS:
        test_instance.assertEqual(run_count, result.statistics.total.all.passed,
                                  'Expected pass count does not match actual pass count.')

    if expected_message:
        for result in result.suite.tests:
            test_instance.assertIn(expected_message, result.message)


def str2bool(val):
    return val.lower() in ("yes", "true", "t", "1")


def timeit(method):
    def timed(*args, **kw):
        result = method(*args, **kw)
        if Settings.timing:
            ts = timer()

            te = timer()
            if 'log_time' in kw:
                name = kw.get('log_name', method.__name__.upper())
                kw['log_time'][name] = int((te - ts) * 1000)
            else:
                BuiltIn().log('%r  %2.2f ms' % \
                              (method.__name__, (te - ts) * 1000), level='DEBUG', console=True)
        return result

    return timed
